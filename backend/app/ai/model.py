from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Tuple

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

from .schemas import (
    ModelMetadata,
    ScheduleSlot,
    ShutdownRecommendation,
    TrainingExample,
    hour_of_week_from_dt,
)


MODEL_DIR = os.environ.get("AI_MODEL_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "models"))
MODEL_BASENAME = "usage_rf_model"
MODEL_VERSION = "1.0.0"


def _ensure_model_dir() -> str:
    os.makedirs(MODEL_DIR, exist_ok=True)
    return MODEL_DIR


def _feature_matrix_and_labels(examples: Iterable[TrainingExample]) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    X_rows: List[List[float]] = []
    y_rows: List[int] = []
    feature_names: List[str] = []

    # Collect union of feature names to maintain consistent column order
    all_feature_names = set()
    ex_list = list(examples)
    for ex in ex_list:
        all_feature_names.update(ex.features.keys())
    feature_names = sorted(list(all_feature_names))

    # Build rows
    for ex in ex_list:
        X_rows.append([float(ex.features.get(fn, 0.0)) for fn in feature_names])
        y_rows.append(int(ex.label))

    if not X_rows:
        return np.zeros((0, 0)), np.zeros((0,)), feature_names
    return np.array(X_rows, dtype=float), np.array(y_rows, dtype=int), feature_names


# PUBLIC_INTERFACE
def train_random_forest(
    examples: Iterable[TrainingExample],
    n_estimators: int = 200,
    max_depth: int | None = None,
    min_samples_leaf: int = 1,
    random_state: int = 42,
) -> Dict[str, str]:
    """
    Train a RandomForest classifier on slot-level usage labels and persist the model.

    Returns:
      - dict with keys: "model_path", "metadata_path", "report"
    """
    X, y, feature_names = _feature_matrix_and_labels(examples)

    if X.shape[0] < 10 or X.shape[1] == 0:
        raise ValueError("Not enough data to train a model. Provide more historical events.")

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=min(0.2, max(0.1, 1.0 / max(10, X.shape[0]))), random_state=random_state, stratify=y
    )

    clf = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_leaf=min_samples_leaf,
        random_state=random_state,
        n_jobs=-1,
        class_weight="balanced_subsample",
    )
    clf.fit(X_train, y_train)

    # Validation report
    y_pred = clf.predict(X_val)
    report = classification_report(y_val, y_pred, output_dict=False)

    # Save artifacts
    _ensure_model_dir()
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    model_path = os.path.join(MODEL_DIR, f"{MODEL_BASENAME}_{ts}.joblib")
    metadata_path = os.path.join(MODEL_DIR, f"{MODEL_BASENAME}_{ts}.meta.json")

    joblib.dump(clf, model_path)

    metadata = ModelMetadata(
        version=MODEL_VERSION,
        created_at=datetime.now(timezone.utc),
        feature_names=feature_names,
        label_name="label",
        slot_minutes=60,
        timezone="UTC",
        population="per_user_instance",
    )
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata.model_dump(mode="json"), f, indent=2)

    return {"model_path": model_path, "metadata_path": metadata_path, "report": report}


def _load_latest_model() -> Tuple[RandomForestClassifier, ModelMetadata]:
    _ensure_model_dir()
    # Find latest model by timestamp suffix
    candidates = [f for f in os.listdir(MODEL_DIR) if f.startswith(MODEL_BASENAME) and f.endswith(".joblib")]
    if not candidates:
        raise FileNotFoundError("No trained model artifacts found.")
    candidates.sort(reverse=True)
    latest_model_path = os.path.join(MODEL_DIR, candidates[0])
    latest_meta_path = latest_model_path.replace(".joblib", ".meta.json")

    clf: RandomForestClassifier = joblib.load(latest_model_path)
    with open(latest_meta_path, "r", encoding="utf-8") as f:
        meta = ModelMetadata(**json.load(f))
    return clf, meta


def _features_from_dt(dt: datetime) -> Dict[str, float]:
    # Rebuild minimal feature set used during training (cyclical + rolling zeros for inference)
    hod = dt.hour
    dow = dt.isoweekday() - 1
    return {
        "hour_sin": float(np.sin(2 * np.pi * hod / 24.0)),
        "hour_cos": float(np.cos(2 * np.pi * hod / 24.0)),
        "dow_sin": float(np.sin(2 * np.pi * dow / 7.0)),
        "dow_cos": float(np.cos(2 * np.pi * dow / 7.0)),
        # Rolling counts unknown at inference; set to 0 which is a neutral assumption
        "rolling_how_count": 0.0,
        "rolling_dow_count": 0.0,
    }


# PUBLIC_INTERFACE
def predict_hourly_week_schedule(
    user_id: str,
    instance_id: str,
    threshold: float = 0.3,
) -> ShutdownRecommendation:
    """
    Produce an hourly schedule for the week (0..167) with predicted usage probabilities.

    Any hour-of-week with predicted probability < threshold is recommended for auto-shutdown.

    Returns:
      ShutdownRecommendation
    """
    clf, meta = _load_latest_model()

    # Build design matrix for each hour-of-week using a reference date week.
    # Use a Monday at 00:00 UTC reference (ISO week).
    reference = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    # Adjust to Monday
    while reference.isoweekday() != 1:
        reference = reference.replace(day=reference.day + 1)

    feature_rows: List[List[float]] = []
    feature_names = list(meta.feature_names)
    hourly_probs: Dict[int, float] = {}

    for i in range(168):
        dt = reference + np.timedelta64(i, "h").astype("timedelta64[ms]").astype(object)
        feats = _features_from_dt(dt)
        # Ensure feature order
        row = [float(feats.get(fn, 0.0)) for fn in feature_names]
        feature_rows.append(row)

    X = np.array(feature_rows, dtype=float)
    # predict_proba may not exist if underlying model lacks it; RandomForestClassifier has it.
    if hasattr(clf, "predict_proba"):
        probs = clf.predict_proba(X)[:, 1]
    else:
        # Fallback: use decision_function scaled via sigmoid-like mapping
        scores = clf.decision_function(X)
        probs = 1 / (1 + np.exp(-scores))

    for i in range(168):
        hourly_probs[i] = float(probs[i])

    shutdown_hours = [i for i, p in hourly_probs.items() if p < threshold]

    return ShutdownRecommendation(
        user_id=user_id,
        instance_id=instance_id,
        threshold=float(threshold),
        hourly_probabilities=hourly_probs,
        shutdown_hours=shutdown_hours,
    )
