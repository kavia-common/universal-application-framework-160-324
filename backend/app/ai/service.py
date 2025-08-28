from __future__ import annotations

from datetime import datetime
from typing import Iterable, List, Sequence

from .features import build_training_data
from .model import predict_hourly_week_schedule, train_random_forest
from .schemas import ShutdownRecommendation, UsageEvent


# PUBLIC_INTERFACE
def ingest_events_from_rows(rows: Sequence[dict]) -> List[UsageEvent]:
    """
    Convert raw dict rows into UsageEvent objects.

    Expected row keys:
      - user_id: str
      - instance_id: str
      - start_time: datetime or ISO string
      - end_time: datetime or ISO string

    Returns:
      List[UsageEvent]
    """
    events: List[UsageEvent] = []
    for r in rows:
        start = r["start_time"]
        end = r["end_time"]
        if isinstance(start, str):
            start = datetime.fromisoformat(start)
        if isinstance(end, str):
            end = datetime.fromisoformat(end)
        events.append(
            UsageEvent(
                user_id=str(r["user_id"]),
                instance_id=str(r["instance_id"]),
                start_time=start,
                end_time=end,
            )
        )
    return events


# PUBLIC_INTERFACE
def train_usage_model_from_events(events: Iterable[UsageEvent]) -> dict:
    """
    Build features from usage events and train the RandomForest model.

    Returns:
      dict containing "model_path", "metadata_path", and "report".
    """
    examples = build_training_data(events)
    return train_random_forest(examples)


# PUBLIC_INTERFACE
def get_shutdown_recommendation(user_id: str, instance_id: str, threshold: float = 0.3) -> ShutdownRecommendation:
    """
    Load the latest trained model and compute the weekly shutdown recommendation for a user/instance.
    """
    return predict_hourly_week_schedule(user_id=user_id, instance_id=instance_id, threshold=threshold)
