from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel, Field


class UsageEvent(BaseModel):
    """
    A usage event denoting a start/stop window for a specific instance and user.
    Times are expected in UTC.
    """
    user_id: str = Field(..., description="User identifier")
    instance_id: str = Field(..., description="Cloud instance identifier")
    start_time: datetime = Field(..., description="UTC start time of usage window")
    end_time: datetime = Field(..., description="UTC end time of usage window (exclusive)")


class TrainingExample(BaseModel):
    """
    A single time-slot labeled example with engineered features and binary label.
    """
    user_id: str
    instance_id: str
    slot_start: datetime = Field(..., description="Start of the time slot (UTC)")
    features: Dict[str, float] = Field(..., description="Engineered numeric features")
    label: int = Field(..., description="1 if used during time slot, else 0")


class ModelMetadata(BaseModel):
    """
    Model metadata stored alongside trained artifacts.
    """
    version: str = Field(..., description="Semantic version for the model")
    created_at: datetime = Field(..., description="UTC time when model was trained")
    feature_names: List[str] = Field(..., description="Ordered feature names used for training")
    label_name: str = Field(default="label", description="Target label name")
    slot_minutes: int = Field(default=60, description="Granularity of time slots in minutes")
    timezone: str = Field(default="UTC", description="Assumed timezone for events")
    population: str = Field(default="per_user_instance", description="Model population scope")


class ScheduleSlot(BaseModel):
    """
    Represents a recommendation for a single recurring hour-of-week slot.
    """
    # 0-167 hour index where 0 = Monday 00:00-01:00 UTC (ISO weekday)
    hour_of_week: int = Field(..., ge=0, le=167, description="Hour-of-week index [0..167], Monday 00:00 = 0")
    probability: float = Field(..., ge=0.0, le=1.0, description="Predicted usage probability for the slot")


class ShutdownRecommendation(BaseModel):
    """
    Recommended schedule for auto-shutdown based on predicted usage likelihood.
    """
    user_id: str = Field(..., description="User identifier")
    instance_id: str = Field(..., description="Instance identifier")
    threshold: float = Field(..., ge=0.0, le=1.0, description="Decision threshold; below this is safe to shutdown")
    # Map hour_of_week -> probability
    hourly_probabilities: Dict[int, float] = Field(..., description="Predicted probability per hour of the week")
    # A list of hours of the week recommended to shutdown (i.e., predicted probability < threshold)
    shutdown_hours: List[int] = Field(..., description="List of hours-of-week recommended for auto-shutdown")


def hour_of_week_from_dt(dt: datetime) -> int:
    """
    Convert a UTC datetime to hour-of-week (0..167) with Monday as 0.
    """
    # isoweekday(): Monday=1..Sunday=7
    day_index = dt.isoweekday() - 1  # 0..6
    return day_index * 24 + dt.hour
