"""
REST API Routes
"""
from flask import Blueprint, jsonify, request, traceback
from app.models.database import get_connection
from app.services.ingestion_service import fetch_and_store_all
from app.services.training_service import retrain_models

api_bp = Blueprint("api", __name__)


@api_bp.route("/health")
def health():
    return jsonify({"status": "ok", "service": "Air Quality Health Risk Prediction"})


@api_bp.route("/readings")
def get_readings():
    city  = request.args.get("city")
    limit = int(request.args.get("limit", 100))
    conn  = get_connection()
    cursor = conn.cursor(dictionary=True)
    if city:
        cursor.execute(
            "SELECT * FROM air_quality_readings WHERE city=%s ORDER BY fetched_at DESC LIMIT %s",
            (city, limit)
        )
    else:
        cursor.execute(
            "SELECT * FROM air_quality_readings ORDER BY fetched_at DESC LIMIT %s",
            (limit,)
        )
    rows = cursor.fetchall()
    cursor.close(); conn.close()
    # Serialize datetime
    for r in rows:
        if r.get("fetched_at"):
            r["fetched_at"] = r["fetched_at"].isoformat()
    return jsonify(rows)


@api_bp.route("/readings/latest")
def get_latest():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.*
        FROM air_quality_readings r
        INNER JOIN (
            SELECT city, MAX(fetched_at) AS max_fa
            FROM air_quality_readings
            GROUP BY city
        ) m ON r.city = m.city AND r.fetched_at = m.max_fa
    """)
    rows = cursor.fetchall()
    cursor.close(); conn.close()
    for r in rows:
        if r.get("fetched_at"):
            r["fetched_at"] = r["fetched_at"].isoformat()
    return jsonify(rows)


# @api_bp.route("/fetch", methods=["POST"])
# def trigger_fetch():
#     """Manually trigger data fetch from all APIs."""
#     n = fetch_and_store_all()
#     return jsonify({"inserted": n, "status": "ok"})


@api_bp.route("/fetch", methods=["POST"])
def trigger_fetch():
    try:
        n = fetch_and_store_all()
        return jsonify({"inserted": n, "status": "ok"}), 200

    except Exception as e:
        traceback.print_exc()  # prints full error in terminal
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@api_bp.route("/train", methods=["POST"])
def trigger_train():
    """Manually trigger model retraining."""
    metrics = retrain_models()
    return jsonify({"status": "ok", "metrics": metrics})


@api_bp.route("/logs")
def get_logs():
    limit = int(request.args.get("limit", 50))
    conn  = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM fetch_logs ORDER BY logged_at DESC LIMIT %s", (limit,))
    rows = cursor.fetchall()
    cursor.close(); conn.close()
    for r in rows:
        if r.get("logged_at"):
            r["logged_at"] = r["logged_at"].isoformat()
    return jsonify(rows)


@api_bp.route("/model-metrics")
def get_model_metrics():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM model_metrics ORDER BY trained_at DESC LIMIT 20")
    rows = cursor.fetchall()
    cursor.close(); conn.close()
    for r in rows:
        if r.get("trained_at"):
            r["trained_at"] = r["trained_at"].isoformat()
    return jsonify(rows)
