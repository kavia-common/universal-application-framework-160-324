from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Iterable, List, Tuple

from sqlalchemy.orm import Session

from .aws import get_ec2_resource
from .config import Settings
from .database import ShutdownLog
from .schemas import EC2Instance

logger = logging.getLogger(__name__)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def list_running_instances(settings: Settings, session_boto, region: str | None = None) -> List[EC2Instance]:
    """
    List all running EC2 instances in the specified or default region.
    """
    ec2 = get_ec2_resource(session_boto, region or settings.aws_default_region)
    result: List[EC2Instance] = []

    for instance in ec2.instances.filter(Filters=[{"Name": "instance-state-name", "Values": ["running"]}]):
        tags_dict = {t["Key"]: t["Value"] for t in (instance.tags or []) if "Key" in t and "Value" in t}
        result.append(
            EC2Instance(
                instance_id=instance.id,
                state=instance.state["Name"],
                instance_type=getattr(instance, "instance_type", None),
                launch_time=getattr(instance, "launch_time", None),
                region=region or settings.aws_default_region,
                tags=tags_dict if tags_dict else None,
            )
        )
    return result


def determine_idle_instances(instances: Iterable[EC2Instance], idle_threshold_minutes: int) -> List[EC2Instance]:
    """
    Determine which instances are idle based on launch_time.
    Note: True CPU/network idleness requires CloudWatch metrics; this approximation uses launch age.
    """
    idle: List[EC2Instance] = []
    threshold = timedelta(minutes=idle_threshold_minutes)
    now = _now_utc()

    for inst in instances:
        # If launch_time is missing, we won't stop it automatically for safety.
        if not inst.launch_time:
            continue
        if (now - inst.launch_time) >= threshold:
            idle.append(inst)
    return idle


def stop_instances_and_log(
    settings: Settings,
    session_boto,
    db: Session,
    instances: Iterable[EC2Instance],
) -> List[Tuple[EC2Instance, bool, str]]:
    """
    Attempt to stop each instance in the list and log the event.

    Returns list of tuples: (instance, success, message)
    """
    results: List[Tuple[EC2Instance, bool, str]] = []
    ec2 = get_ec2_resource(session_boto, settings.aws_default_region)
    for inst in instances:
        try:
            logger.info("Stopping instance %s in region %s", inst.instance_id, inst.region)
            ec2.Instance(inst.instance_id).stop()
            reason = "Auto-shutdown due to idleness threshold exceeded"
            details = f"Instance launch_time={inst.launch_time}, threshold_minutes={settings.idle_threshold_minutes}"
            log = ShutdownLog(
                instance_id=inst.instance_id,
                region=inst.region,
                reason=reason,
                details=details,
            )
            db.add(log)
            results.append((inst, True, "stop initiated"))
        except Exception as e:
            logger.exception("Failed to stop instance %s: %s", inst.instance_id, e)
            results.append((inst, False, str(e)))
    return results
