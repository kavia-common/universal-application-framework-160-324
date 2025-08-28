from __future__ import annotations

import logging
import os
from typing import Annotated, Optional, List

from fastapi import Depends, FastAPI, HTTPException, Query, Body
from fastapi.responses import JSONResponse

from .config import Settings, get_settings
from .aws import get_boto3_session
from .database import init_db, db_session, ShutdownLog
from .scheduler import IdleShutdownScheduler
from .services import list_running_instances, determine_idle_instances, stop_instances_and_log
from .schemas import EC2InstanceListResponse, EC2Instance, ShutdownEvent
from .ai.service import (
    ingest_events_from_rows,
    train_usage_model_from_events,
    get_shutdown_recommendation,
)

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("ec2-manager")

app = FastAPI(
    title="EC2 Manager API",
    description=(
        "FastAPI backend to list running EC2 instances, automatically stop idle instances, "
        "log shutdown events into PostgreSQL, and provide AI-based auto-shutdown recommendations."
    ),
    version="1.1.0",
    openapi_tags=[
        {"name": "instances", "description": "Operations related to EC2 instances"},
        {"name": "maintenance", "description": "Operational and background tasks"},
        {"name": "ai", "description": "AI/ML training and recommendation endpoints"},
        {"name": "docs", "description": "API and realtime usage information"},
    ],
)

# Start lightweight scheduler
_scheduler: Optional[IdleShutdownScheduler] = None


def boto_session_dep(settings: Annotated[Settings, Depends(get_settings)]):
    """
    Dependency to provide a configured boto3 session.
    """
    return get_boto3_session(settings)


@app.on_event("startup")
def on_startup():
    """
    Initialize database and start the background idle shutdown scheduler.
    """
    global _scheduler
    try:
        init_db()
        settings = get_settings()
        _scheduler = IdleShutdownScheduler(settings)
        _scheduler.start()
        logger.info("Application startup complete.")
    except Exception as e:
        logger.exception("Startup initialization failed: %s", e)
        # Allow app to start even if scheduler fails; DB init is critical though.


@app.on_event("shutdown")
def on_shutdown():
    """
    Stop background scheduler gracefully.
    """
    global _scheduler
    try:
        if _scheduler:
            _scheduler.stop()
    except Exception as e:
        logger.exception("Shutdown error: %s", e)


# PUBLIC_INTERFACE
@app.get(
    "/health",
    summary="Health check",
    description="Simple health check endpoint.",
    tags=["docs"],
)
def health():
    """
    Health check endpoint.

    Returns 200 OK if the service is running.
    """
    return {"status": "ok"}


# PUBLIC_INTERFACE
@app.get(
    "/instances/running",
    response_model=EC2InstanceListResponse,
    summary="List running EC2 instances",
    description="Returns all running EC2 instances for the configured or specified region.",
    tags=["instances"],
)
def list_running(
    settings: Annotated[Settings, Depends(get_settings)],
    session_boto=Depends(boto_session_dep),
    region: Optional[str] = Query(default=None, description="AWS region override"),
):
    """
    List running EC2 instances.

    Parameters:
      - region: Optional AWS region to query; defaults to settings.aws_default_region

    Returns:
      - EC2InstanceListResponse with count and list of EC2Instance
    """
    try:
        instances: List[EC2Instance] = list_running_instances(settings, session_boto, region=region)
        return EC2InstanceListResponse(count=len(instances), instances=instances)
    except Exception as e:
        logger.exception("Failed to list instances: %s", e)
        raise HTTPException(status_code=500, detail="Failed to list instances")


# PUBLIC_INTERFACE
@app.post(
    "/maintenance/idle-shutdown",
    summary="Trigger idle instance shutdown",
    description=(
        "Manually trigger the idle shutdown process. "
        "Identifies instances whose launch_time exceeds the configured idle threshold "
        "and initiates a stop, logging events to the database."
    ),
    tags=["maintenance"],
    response_model=List[ShutdownEvent],
)
def trigger_idle_shutdown(
    settings: Annotated[Settings, Depends(get_settings)],
    session_boto=Depends(boto_session_dep),
):
    """
    Trigger the idle shutdown process on demand.

    Returns:
      - List of ShutdownEvent for successfully logged shutdowns
    """
    try:
        running: List[EC2Instance] = list_running_instances(settings, session_boto)
        idle = determine_idle_instances(running, settings.idle_threshold_minutes)
        events: List[ShutdownEvent] = []
        if not idle:
            return events

        with db_session() as db:
            results = stop_instances_and_log(settings, session_boto, db, idle)
            # Build response only for successfully logged events
            for inst, ok, msg in results:
                if ok:
                    events.append(
                        ShutdownEvent(
                            instance_id=inst.instance_id,
                            region=inst.region,
                            reason="Auto-shutdown due to idleness threshold exceeded",
                            details=f"{msg}; launch_time={inst.launch_time}",
                            event_time=None,  # DB value will be set; we return later with DB timestamps if available
                        )
                    )
        # Fetch last events with DB timestamps for accuracy
        with db_session() as db:
            db_events = (
                db.query(ShutdownLog)
                .order_by(ShutdownLog.event_time.desc())
                .limit(len(events))
                .all()
            )
            # Map to response models; if fewer rows exist, fallback to current response content
            response: List[ShutdownEvent] = []
            for log in db_events:
                response.append(
                    ShutdownEvent(
                        instance_id=log.instance_id,
                        region=log.region,
                        reason=log.reason,
                        details=log.details,
                        event_time=log.event_time,
                    )
                )
            if response:
                return response
        return events
    except Exception as e:
        logger.exception("Idle shutdown trigger failed: %s", e)
        raise HTTPException(status_code=500, detail="Idle shutdown trigger failed")


# PUBLIC_INTERFACE
@app.get(
    "/logs/shutdowns",
    summary="List shutdown logs",
    description="List recent EC2 shutdown events from the database.",
    tags=["maintenance"],
)
def list_shutdown_logs(limit: int = Query(default=50, ge=1, le=1000)):
    """
    List recent shutdown events stored in the database.

    Parameters:
      - limit: number of records to return (1..1000)

    Returns:
      - JSON array of shutdown log entries
    """
    try:
        with db_session() as db:
            rows = db.query(ShutdownLog).order_by(ShutdownLog.event_time.desc()).limit(limit).all()
            return [
                {
                    "instance_id": r.instance_id,
                    "region": r.region,
                    "reason": r.reason,
                    "details": r.details,
                    "event_time": r.event_time.isoformat(),
                }
                for r in rows
            ]
    except Exception as e:
        logger.exception("Failed to list shutdown logs: %s", e)
        raise HTTPException(status_code=500, detail="Failed to list shutdown logs")


# PUBLIC_INTERFACE
@app.get(
    "/docs/websocket-usage",
    summary="WebSocket/Realtime usage",
    description=(
        "This project does not currently expose real-time WebSockets. "
        "The background scheduler runs server-side at a configured interval."
    ),
    tags=["docs"],
)
def websocket_usage_note():
    """
    Returns a note regarding real-time usage.

    There are no WebSocket endpoints in this service.
    """
    return JSONResponse(
        content={
            "note": "No WebSocket endpoints are available. Background idle shutdown runs on the server."
        }
    )


# PUBLIC_INTERFACE
@app.post(
    "/ai/train-usage-model",
    summary="Train usage model from historical events",
    description=(
        "Train an interpretable RandomForest model using historical start/stop usage windows. "
        "Provide a JSON array of events with fields: user_id, instance_id, start_time, end_time (ISO strings). "
        "Artifacts are persisted to disk and the latest will be used for inference."
    ),
    tags=["ai"],
)
def ai_train_usage_model(
    events: list[dict] = Body(
        default=...,
        description="Array of usage events: [{user_id, instance_id, start_time, end_time}]",
    )
):
    """
    Train the usage model.

    Parameters:
      - events: List of dictionaries with keys user_id, instance_id, start_time, end_time (ISO timestamps)

    Returns:
      - Object with model artifact paths and a validation classification report.
    """
    try:
        usage_events = ingest_events_from_rows(events)
        result = train_usage_model_from_events(usage_events)
        return result
    except Exception as e:
        logger.exception("AI training failed: %s", e)
        raise HTTPException(status_code=400, detail=f"Training failed: {e}")


# PUBLIC_INTERFACE
@app.get(
    "/ai/recommendation",
    summary="Get weekly auto-shutdown recommendation",
    description=(
        "Returns an hourly-of-week (0..167) probability map of expected usage and recommended shutdown hours "
        "for the given user_id and instance_id. Requires a trained model to exist."
    ),
    tags=["ai"],
)
def ai_get_recommendation(
    user_id: str = Query(..., description="User identifier"),
    instance_id: str = Query(..., description="Instance identifier"),
    threshold: float = Query(0.3, ge=0.0, le=1.0, description="Threshold below which to recommend shutdown"),
):
    """
    Produce an auto-shutdown schedule.

    Parameters:
      - user_id: user identifier
      - instance_id: instance identifier
      - threshold: probability cutoff for shutdown recommendation

    Returns:
      - ShutdownRecommendation object with hourly probabilities and recommended shutdown hours.
    """
    try:
        rec = get_shutdown_recommendation(user_id=user_id, instance_id=instance_id, threshold=threshold)
        return rec.model_dump(mode="json")
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("AI recommendation failed: %s", e)
        raise HTTPException(status_code=500, detail="Failed to compute recommendation")
