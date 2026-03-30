"""
Machine Learning Pipeline
- Feature engineering
- Model training: Random Forest, Gradient Boosting, XGBoost, LSTM
- Comparative analysis
- Prediction with confidence scores
"""
import os
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_absolute_error, mean_squared_error
)
from sklearn.pipeline import Pipeline
import joblib

logger = logging.getLogger(__name__)

MODEL_DIR = os.path.join(os.path.dirname(__file__), "../../models_store")
os.makedirs(MODEL_DIR, exist_ok=True)

# AQI → risk level mapping
RISK_THRESHOLDS = [
    (0,   50,  "Good"),
    (51,  100, "Moderate"),
    (101, 150, "Unhealthy for Sensitive Groups"),
    (151, 200, "Unhealthy"),
    (201, 300, "Very Unhealthy"),
    (301, 999, "Hazardous"),
]

FEATURE_COLS = ["aqi", "pm25", "pm10", "o3", "no2", "so2", "co",
                "temperature", "humidity", "wind_speed"]


def aqi_to_risk(aqi: float) -> str:
    if aqi is None:
        return "Unknown"
    for lo, hi, label in RISK_THRESHOLDS:
        if lo <= aqi <= hi:
            return label
    return "Hazardous"


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and engineer features from raw readings."""
    df = df.copy()
    df = df[FEATURE_COLS + ["fetched_at", "city"]].copy()

    # Fill missing values with column medians
    for col in FEATURE_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col].fillna(df[col].median(), inplace=True)

    # Time features
    df["fetched_at"] = pd.to_datetime(df["fetched_at"])
    df["hour"]       = df["fetched_at"].dt.hour
    df["dayofweek"]  = df["fetched_at"].dt.dayofweek

    # Derived features
    df["pm_ratio"]   = df["pm25"] / (df["pm10"] + 1e-9)
    df["heat_index"] = df["temperature"] * df["humidity"] / 100

    # Target
    df["risk_level"] = df["aqi"].apply(aqi_to_risk)

    return df


def get_feature_matrix(df: pd.DataFrame):
    """Return X, y arrays from preprocessed dataframe."""
    extra = ["hour", "dayofweek", "pm_ratio", "heat_index"]
    features = FEATURE_COLS + extra
    X = df[features].values
    y = df["risk_level"].values
    return X, y, features


def train_all_models(df: pd.DataFrame) -> dict:
    """
    Train Random Forest, Gradient Boosting on the provided dataframe.
    Returns dict of model_name → metrics.
    """
    df = preprocess(df)
    X, y, features = get_feature_matrix(df)

    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
    )

    models = {
        "RandomForest": Pipeline([
            ("scaler", StandardScaler()),
            ("clf",    RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)),
        ]),
        "GradientBoosting": Pipeline([
            ("scaler", StandardScaler()),
            ("clf",    GradientBoostingClassifier(n_estimators=150, learning_rate=0.1, random_state=42)),
        ]),
    }

    # Try XGBoost if available
    try:
        from xgboost import XGBClassifier
        models["XGBoost"] = Pipeline([
            ("scaler", StandardScaler()),
            ("clf",    XGBClassifier(n_estimators=150, use_label_encoder=False,
                                     eval_metric="mlogloss", random_state=42)),
        ])
    except ImportError:
        logger.info("[ML] XGBoost not installed, skipping.")

    results = {}
    for name, pipeline in models.items():
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)

        acc  = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        rec  = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        f1   = f1_score(y_test, y_pred, average="weighted", zero_division=0)
        mae  = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))

        # Save model
        model_path = os.path.join(MODEL_DIR, f"{name}.pkl")
        joblib.dump({"pipeline": pipeline, "label_encoder": le, "features": features}, model_path)

        results[name] = {
            "accuracy":        round(acc,  4),
            "precision_score": round(prec, 4),
            "recall_score":    round(rec,  4),
            "f1_score":        round(f1,   4),
            "mae":             round(mae,  4),
            "rmse":            round(rmse, 4),
        }
        logger.info(f"[ML] {name} → acc={acc:.3f} f1={f1:.3f}")

    return results


def predict(city: str, latest_row: dict) -> list[dict]:
    """
    Run prediction for a city using all saved models.
    Returns list of prediction dicts.
    """
    predictions = []
    for model_file in os.listdir(MODEL_DIR):
        if not model_file.endswith(".pkl"):
            continue
        model_name = model_file.replace(".pkl", "")
        try:
            bundle   = joblib.load(os.path.join(MODEL_DIR, model_file))
            pipeline = bundle["pipeline"]
            le       = bundle["label_encoder"]
            features = bundle["features"]

            df = pd.DataFrame([latest_row])
            df["fetched_at"] = pd.to_datetime(df.get("fetched_at", datetime.utcnow()))
            df["hour"]       = df["fetched_at"].dt.hour
            df["dayofweek"]  = df["fetched_at"].dt.dayofweek
            df["pm_ratio"]   = df["pm25"].fillna(0) / (df["pm10"].fillna(0) + 1e-9)
            df["heat_index"] = df["temperature"].fillna(25) * df["humidity"].fillna(50) / 100

            for col in FEATURE_COLS:
                if col not in df.columns:
                    df[col] = 0

            X = df[features].fillna(0).values
            y_enc = pipeline.predict(X)[0]
            risk  = le.inverse_transform([y_enc])[0]

            # Confidence via predict_proba if available
            confidence = None
            try:
                proba      = pipeline.predict_proba(X)[0]
                confidence = round(float(max(proba)), 4)
            except Exception:
                pass

            # Risk score: 0-100
            risk_map = {"Good": 10, "Moderate": 30, "Unhealthy for Sensitive Groups": 50,
                        "Unhealthy": 70, "Very Unhealthy": 85, "Hazardous": 100}
            risk_score = risk_map.get(risk, 50)

            predictions.append({
                "city":         city,
                "model_name":   model_name,
                "risk_level":   risk,
                "risk_score":   risk_score,
                "confidence":   confidence,
                "features_used": json.dumps(features),
                "predicted_at": datetime.utcnow(),
            })

        except Exception as e:
            logger.error(f"[ML] Prediction error for {model_name}: {e}")

    return predictions
