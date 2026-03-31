'PYEOF'
from flask import Blueprint, jsonify, request
from app.models.database import get_connection
from app.services.ingestion_service import fetch_and_store_all
from app.services.training_service import retrain_models

api_bp = Blueprint("api", __name__)

def serialize(rows):
    for r in rows:
        for k, v in r.items():
            if hasattr(v, 'isoformat'):
                r[k] = v.isoformat()
    return rows

@api_bp.route("/health")
def health():
    return jsonify({"status": "ok", "service": "Air Quality Health Risk Prediction"})

@api_bp.route("/readings")
def get_readings():
    city  = request.args.get("city")
    limit = int(request.args.get("limit", 100))
    conn  = get_connection()
    cur   = conn.cursor(dictionary=True)
    if city:
        cur.execute("SELECT * FROM air_quality_readings WHERE city=%s ORDER BY timestamp_utc DESC LIMIT %s", (city, limit))
    else:
        cur.execute("SELECT * FROM air_quality_readings ORDER BY timestamp_utc DESC LIMIT %s", (limit,))
    rows = cur.fetchall(); cur.close(); conn.close()
    return jsonify(serialize(rows))

@api_bp.route("/readings/latest")
def get_latest():
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT r.* FROM air_quality_readings r
        INNER JOIN (
            SELECT city, MAX(timestamp_utc) AS mt
            FROM air_quality_readings GROUP BY city
        ) m ON r.city=m.city AND r.timestamp_utc=m.mt
    """)
    rows = cur.fetchall(); cur.close(); conn.close()
    return jsonify(serialize(rows))

@api_bp.route("/fetch", methods=["POST"])
def trigger_fetch():
    try:
        n = fetch_and_store_all()
        return jsonify({"inserted": n, "status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route("/train", methods=["POST"])
def trigger_train():
    try:
        metrics = retrain_models()
        return jsonify({"status": "ok", "metrics": metrics})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route("/logs")
def get_logs():
    limit = int(request.args.get("limit", 50))
    conn  = get_connection()
    cur   = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM fetch_logs ORDER BY logged_at DESC LIMIT %s", (limit,))
    rows  = cur.fetchall(); cur.close(); conn.close()
    return jsonify(serialize(rows))

@api_bp.route("/model-metrics")
def get_model_metrics():
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM model_metrics ORDER BY trained_at DESC LIMIT 20")
    rows = cur.fetchall(); cur.close(); conn.close()
    return jsonify(serialize(rows))
PYEOF