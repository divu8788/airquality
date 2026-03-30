"""
Prediction API Routes
"""
from flask import Blueprint, jsonify, request
from app.models.database import get_connection
from app.services.prediction_service import run_predictions_all_cities

predictions_bp = Blueprint("predictions", __name__)


@predictions_bp.route("/")
def get_predictions():
    city  = request.args.get("city")
    limit = int(request.args.get("limit", 50))
    conn  = get_connection()
    cursor = conn.cursor(dictionary=True)
    if city:
        cursor.execute(
            "SELECT * FROM health_predictions WHERE city=%s ORDER BY predicted_at DESC LIMIT %s",
            (city, limit)
        )
    else:
        cursor.execute(
            "SELECT * FROM health_predictions ORDER BY predicted_at DESC LIMIT %s",
            (limit,)
        )
    rows = cursor.fetchall()
    cursor.close(); conn.close()
    for r in rows:
        if r.get("predicted_at"):
            r["predicted_at"] = r["predicted_at"].isoformat()
        if r.get("features_used") and isinstance(r["features_used"], (bytes, bytearray)):
            r["features_used"] = r["features_used"].decode()
    return jsonify(rows)


@predictions_bp.route("/run", methods=["POST"])
def trigger_predictions():
    run_predictions_all_cities()
    return jsonify({"status": "ok"})


@predictions_bp.route("/latest")
def latest_predictions():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.*
        FROM health_predictions p
        INNER JOIN (
            SELECT city, MAX(predicted_at) AS mp
            FROM health_predictions
            GROUP BY city
        ) m ON p.city = m.city AND p.predicted_at = m.mp
    """)
    rows = cursor.fetchall()
    cursor.close(); conn.close()
    for r in rows:
        if r.get("predicted_at"):
            r["predicted_at"] = r["predicted_at"].isoformat()
    return jsonify(rows)
