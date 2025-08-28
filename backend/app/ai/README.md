# Usage-based Auto-shutdown AI Module

This module ingests historical instance usage windows (start/stop times), engineers time features, trains an interpretable model, and produces weekly shutdown recommendations.

## Data Model

- UsageEvent: { user_id, instance_id, start_time, end_time } (UTC)
- TrainingExample: slot-level example with engineered features and label
- ShutdownRecommendation: hourly-of-week probabilities and shutdown hours (< threshold)

## Features

- Cyclical encodings for hour-of-day and day-of-week
- Rolling usage counts per hour-of-week and day-of-week
- Slot granularity: 60 minutes
- Model: RandomForestClassifier with class_weight=balanced_subsample

## Persistence

- Artifacts saved to AI_MODEL_DIR (default: backend/app/models/)
- Files:
  - usage_rf_model_<timestamp>.joblib
  - usage_rf_model_<timestamp>.meta.json

## Integration

- Functions:
  - ingest_events_from_rows(rows) -> List[UsageEvent]
  - train_usage_model_from_events(events) -> dict
  - get_shutdown_recommendation(user_id, instance_id, threshold) -> ShutdownRecommendation

- API endpoints (added in app/main.py):
  - POST /ai/train-usage-model  (body: list of events)
  - GET  /ai/recommendation?user_id=...&instance_id=...&threshold=0.3

## Example

POST /ai/train-usage-model
[
  {"user_id": "u1", "instance_id": "i-123", "start_time": "2024-08-05T09:00:00+00:00", "end_time": "2024-08-05T12:00:00+00:00"},
  {"user_id": "u1", "instance_id": "i-123", "start_time": "2024-08-06T10:00:00+00:00", "end_time": "2024-08-06T11:30:00+00:00"}
]

GET /ai/recommendation?user_id=u1&instance_id=i-123&threshold=0.3

Returns hourly probabilities for 168 hours and a list of recommended shutdown hours.
