import os
import logging
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, mean_absolute_error
from sklearn.pipeline import Pipeline
import joblib

log      = logging.getLogger(__name__)
MDL_DIR  = os.path.join(os.path.dirname(__file__), "../../model_store")
os.makedirs(MDL_DIR, exist_ok=True)

FEATURES = ["aqi", "pm25", "pm10", "o3", "no2", "so2", "co",
            "temperature", "humidity", "wind_speed"]

RISK_MAP = [
    (0,   50,  "Good"),
    (51,  100, "Moderate"),
    (101, 150, "Unhealthy for Sensitive Groups"),
    (151, 200, "Unhealthy"),
    (201, 300, "Very Unhealthy"),
    (301, 9999,"Hazardous"),
]

SCORE_MAP = {
    "Good": 10, "Moderate": 35,
    "Unhealthy for Sensitive Groups": 55,
    "Unhealthy": 70, "Very Unhealthy": 85, "Hazardous": 100,
}


def aqi_to_risk(aqi):
    if aqi is None:
        return "Unknown"
    for lo, hi, label in RISK_MAP:
        if lo <= float(aqi) <= hi:
            return label
    return "Hazardous"


def _build_X(df):
    df = df.copy()
    for col in FEATURES:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col].fillna(df[col].median(), inplace=True)
    df["pm_ratio"]   = df["pm25"] / (df["pm10"] + 1e-6)
    df["heat_index"] = df["temperature"].fillna(20) * df["humidity"].fillna(50) / 100
    all_cols = FEATURES + ["pm_ratio", "heat_index"]
    return df[all_cols].values, all_cols


def train(df):
    df       = df.copy()
    df["risk"] = df["aqi"].apply(aqi_to_risk)
    df         = df[df["risk"] != "Unknown"]

    X, cols = _build_X(df)
    le      = LabelEncoder()
    y       = le.fit_transform(df["risk"].values)

    if len(set(y)) < 2:
        log.warning("[ML] Need at least 2 risk classes to train.")
        return {}

    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)

    models = {
        "RandomForest": Pipeline([
            ("sc", StandardScaler()),
            ("cl", RandomForestClassifier(n_estimators=150, random_state=42, n_jobs=-1)),
        ]),
        "GradientBoosting": Pipeline([
            ("sc", StandardScaler()),
            ("cl", GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, random_state=42)),
        ]),
    }

    try:
        from xgboost import XGBClassifier
        models["XGBoost"] = Pipeline([
            ("sc", StandardScaler()),
            ("cl", XGBClassifier(n_estimators=100, eval_metric="mlogloss",
                                 use_label_encoder=False, random_state=42)),
        ])
    except ImportError:
        pass

    results = {}
    for name, pipe in models.items():
        pipe.fit(X_tr, y_tr)
        y_pred = pipe.predict(X_te)
        metrics = {
            "accuracy":   round(accuracy_score(y_te, y_pred), 4),
            "f1":         round(f1_score(y_te, y_pred, average="weighted", zero_division=0), 4),
            "precision_": round(precision_score(y_te, y_pred, average="weighted", zero_division=0), 4),
            "recall":     round(recall_score(y_te, y_pred, average="weighted", zero_division=0), 4),
            "mae":        round(mean_absolute_error(y_te, y_pred), 4),
            "rmse":       round(float(np.sqrt(np.mean((y_te - y_pred) ** 2))), 4),
            "rows_used":  len(df),
        }
        joblib.dump({"pipe": pipe, "le": le, "cols": cols},
                    os.path.join(MDL_DIR, name + ".pkl"))
        results[name] = metrics
        log.info("[ML] %s trained — acc=%.3f f1=%.3f", name, metrics["accuracy"], metrics["f1"])

    return results


def predict_city(city_name, row):
    results = []
    for fname in os.listdir(MDL_DIR):
        if not fname.endswith(".pkl"):
            continue
        model_name = fname.replace(".pkl", "")
        try:
            bundle = joblib.load(os.path.join(MDL_DIR, fname))
            pipe   = bundle["pipe"]
            le     = bundle["le"]
            cols   = bundle["cols"]

            df = pd.DataFrame([row])
            for c in FEATURES:
                if c not in df.columns:
                    df[c] = 0
                df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
            df["pm_ratio"]   = df["pm25"] / (df["pm10"] + 1e-6)
            df["heat_index"] = df["temperature"].fillna(20) * df["humidity"].fillna(50) / 100

            X        = df[cols].values
            y_enc    = pipe.predict(X)[0]
            risk     = le.inverse_transform([y_enc])[0]
            conf     = None
            try:
                proba = pipe.predict_proba(X)[0]
                conf  = round(float(max(proba)), 4)
            except Exception:
                pass

            results.append({
                "city":        city_name,
                "model":       model_name,
                "risk_level":  risk,
                "risk_score":  SCORE_MAP.get(risk, 50),
                "confidence":  conf,
                "predicted_at": datetime.utcnow(),
            })
        except Exception as e:
            log.error("[ML] predict error %s: %s", model_name, e)
    return results
