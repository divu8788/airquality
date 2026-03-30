"""
Training Service - pulls historical readings from DB and retrains all ML models.
"""
import logging
import pandas as pd
from flask import current_app
from app.models.database import get_connection
from app.ml.predictor import train_all_models
from datetime import datetime

logger = logging.getLogger(__name__)


def retrain_models():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM air_quality_readings ORDER BY fetched_at DESC LIMIT 10000")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    if len(rows) < 50:
        logger.warning("[Training] Not enough data to train (<50 rows). Skipping.")
        return

    df = pd.DataFrame(rows)
    metrics = train_all_models(df)

    # Store metrics in DB
    conn = get_connection()
    ins = conn.cursor()
    for model_name, m in metrics.items():
        ins.execute("""
            INSERT INTO model_metrics
                (model_name, accuracy, precision_score, recall_score,
                 f1_score, mae, rmse, trained_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            model_name, m["accuracy"], m["precision_score"], m["recall_score"],
            m["f1_score"], m["mae"], m["rmse"], datetime.utcnow()
        ))
    ins.close()
    conn.close()

    logger.info(f"[Training] Models retrained: {list(metrics.keys())}")
    return metrics
