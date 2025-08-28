from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, Iterable, List, Tuple

import math

from .schemas import UsageEvent, TrainingExample, hour_of_week_from_dt


DEFAULT_SLOT_MINUTES = 60


@dataclass(frozen=True)
class SlotKey:
    user_id: str
    instance_id: str
    slot_start: datetime  # UTC, aligned to slot boundary


def _align_to_slot_start(dt: datetime, slot_minutes: int) -> datetime:
    """
    Align a datetime to the start of its slot boundary in UTC.
    """
    if dt.tzinfo is None:
        # Assume UTC if naive
        dt = dt.replace(tzinfo=timezone.utc)
    minutes = (dt.minute // slot_minutes) * slot_minutes
    return dt.replace(minute=0, second=0, microsecond=0) + timedelta(minutes=minutes)


def _iter_slots(start: datetime, end: datetime, slot_minutes: int) -> Iterable[datetime]:
    """
    Yield slot starts in [start, end) at given granularity, aligned to slot boundaries.
    """
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)

    cur = _align_to_slot_start(start, slot_minutes)
    while cur < end:
        yield cur
        cur += timedelta(minutes=slot_minutes)


def _cyclical_features(hour: int, day_of_week: int) -> Dict[str, float]:
    """
    Create cyclical encoding for hour of day and day of week.
    """
    hod = hour % 24
    dow = day_of_week % 7
    return {
        "hour_sin": math.sin(2 * math.pi * hod / 24.0),
        "hour_cos": math.cos(2 * math.pi * hod / 24.0),
        "dow_sin": math.sin(2 * math.pi * dow / 7.0),
        "dow_cos": math.cos(2 * math.pi * dow / 7.0),
    }


def build_training_data(
    events: Iterable[UsageEvent],
    slot_minutes: int = DEFAULT_SLOT_MINUTES,
    min_history_days: int = 7,
) -> List[TrainingExample]:
    """
    Convert usage events into labeled slot examples with engineered features.

    Feature set:
      - Cyclical hour-of-day and day-of-week encodings
      - Hour-of-week one-hot (optional; omitted for model simplicity)
      - Rolling usage counts per hour-of-week and day-of-week
      - Binary label: 1 if slot is used (overlaps any event), else 0

    The function infers the total observation window from min/max event times and
    generates all slots across the window per user/instance for balanced training.

    Returns a list of TrainingExample instances.
    """
    events_list = list(events)
    if not events_list:
        return []

    # Group events by (user, instance)
    grouped: Dict[Tuple[str, str], List[UsageEvent]] = defaultdict(list)
    global_min = None
    global_max = None
    for ev in events_list:
        grouped[(ev.user_id, ev.instance_id)].append(ev)
        global_min = ev.start_time if global_min is None else min(global_min, ev.start_time)
        global_max = ev.end_time if global_max is None else max(global_max, ev.end_time)

    if global_min is None or global_max is None:
        return []

    # Ensure timezone-aware UTC
    if global_min.tzinfo is None:
        global_min = global_min.replace(tzinfo=timezone.utc)
    if global_max.tzinfo is None:
        global_max = global_max.replace(tzinfo=timezone.utc)

    # Ensure a minimum history window
    min_window_end = global_min + timedelta(days=min_history_days)
    if global_max < min_window_end:
        global_max = min_window_end

    examples: List[TrainingExample] = []

    for (user_id, instance_id), evs in grouped.items():
        # Build a quick lookup for slots that were used
        used_slots = set()
        for ev in evs:
            for slot_start in _iter_slots(ev.start_time, ev.end_time, slot_minutes):
                used_slots.add(slot_start)

        # Rolling aggregates: counts by hour_of_week and day_of_week for prior usage
        rolling_count_how: Dict[int, int] = defaultdict(int)
        rolling_count_dow: Dict[int, int] = defaultdict(int)

        # Iterate slots over the observation window
        for slot_start in _iter_slots(global_min, global_max, slot_minutes):
            label = 1 if slot_start in used_slots else 0

            # Build features
            dt = slot_start
            # ISO weekday: Monday=1..Sunday=7
            dow = dt.isoweekday() - 1
            hod = dt.hour
            how = hour_of_week_from_dt(dt)

            cyc = _cyclical_features(hod, dow)
            features = {
                **cyc,
                "rolling_how_count": float(rolling_count_how[how]),
                "rolling_dow_count": float(rolling_count_dow[dow]),
            }

            examples.append(
                TrainingExample(
                    user_id=user_id,
                    instance_id=instance_id,
                    slot_start=slot_start,
                    features=features,
                    label=label,
                )
            )

            # Update rolling counts after labeling to avoid leakage
            if label == 1:
                rolling_count_how[how] += 1
                rolling_count_dow[dow] += 1

    return examples
