"""
Prediction Service - runs ML inference on latest readings and stores results.
"""
import logging
from flask import current_app
from app.models.database import get_connection
from app.ml.predictor import predict

logger = logging.getLogger(__name__)


def run_predictions_all_cities():
    cities = current_app.config["MONITORED_CITIES"]
    conn = get_connection()

    for city in cities:
        name = city["name"]
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM air_quality_readings
            WHERE city = %s
            ORDER BY fetched_at DESC
            LIMIT 1
        """, (name,))
        row = cursor.fetchone()
        cursor.close()

        if not row:
            logger.warning(f"[PredictionService] No data for {name}, skipping.")
            continue

        preds = predict(name, row)
        ins_cursor = conn.cursor()
        for p in preds:
            ins_cursor.execute("""
                INSERT INTO health_predictions
                    (city, model_name, risk_level, risk_score, confidence,
                     features_used, predicted_at)
                VALUES
                    (%(city)s, %(model_name)s, %(risk_level)s, %(risk_score)s,
                     %(confidence)s, %(features_used)s, %(predicted_at)s)
            """, p)
        ins_cursor.close()
        logger.info(f"[PredictionService] {len(preds)} predictions stored for {name}")

    conn.close()
