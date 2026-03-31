from flask import Blueprint, jsonify, request
from datetime import datetime
from app.models.database import get_db
from app.services.ingestion import run as ingest
from app.ml.predictor import train, predict_city

api_bp = Blueprint("api", __name__)


def _serial(rows):
    for r in rows:
        for k, v in r.items():
            if isinstance(v, datetime):
                r[k] = v.isoformat()
    return rows


# ── Health ────────────────────────────────────────────────────────────────────
@api_bp.route("/health")
def health():
    return jsonify({"status": "ok"})


# ── Readings ──────────────────────────────────────────────────────────────────
@api_bp.route("/readings")
def readings():
    city  = request.args.get("city")
    limit = int(request.args.get("limit", 100))
    conn  = get_db()
    cur   = conn.cursor(dictionary=True)
    if city:
        cur.execute("SELECT * FROM readings WHERE city=%s ORDER BY fetched_at DESC LIMIT %s", (city, limit))
    else:
        cur.execute("SELECT * FROM readings ORDER BY fetched_at DESC LIMIT %s", (limit,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(_serial(rows))


@api_bp.route("/readings/latest")
def readings_latest():
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT r.* FROM readings r
        INNER JOIN (
            SELECT city, MAX(fetched_at) mt FROM readings GROUP BY city
        ) m ON r.city = m.city AND r.fetched_at = m.mt
    """)
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(_serial(rows))


# ── Fetch ─────────────────────────────────────────────────────────────────────
@api_bp.route("/fetch", methods=["POST"])
def fetch():
    try:
        n = ingest()
        return jsonify({"status": "ok", "inserted": n})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ── Train ─────────────────────────────────────────────────────────────────────
@api_bp.route("/train", methods=["POST"])
def train_models():
    try:
        import pandas as pd
        conn = get_db()
        cur  = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM readings ORDER BY fetched_at DESC LIMIT 10000")
        rows = cur.fetchall()
        cur.close(); conn.close()

        if len(rows) < 30:
            return jsonify({"status": "error",
                            "message": "Need at least 30 rows. Have: " + str(len(rows))}), 400

        df      = pd.DataFrame(rows)
        metrics = train(df)

        conn = get_db()
        cur  = conn.cursor()
        for mname, m in metrics.items():
            cur.execute("""
                INSERT INTO model_metrics
                    (model, accuracy, f1, precision_, recall, mae, rmse, rows_used)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (mname, m["accuracy"], m["f1"], m["precision_"],
                  m["recall"], m["mae"], m["rmse"], m["rows_used"]))
        cur.close(); conn.close()
        return jsonify({"status": "ok", "metrics": metrics})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ── Predict ───────────────────────────────────────────────────────────────────
@api_bp.route("/predict", methods=["POST"])
def predict():
    try:
        from flask import current_app
        cities = current_app.config["CITIES"]
        conn   = get_db()
        cur    = conn.cursor(dictionary=True)
        total  = 0

        for city in cities:
            name = city["name"]
            cur.execute(
                "SELECT * FROM readings WHERE city=%s ORDER BY fetched_at DESC LIMIT 1",
                (name,)
            )
            row = cur.fetchone()
            if not row:
                continue
            preds = predict_city(name, row)
            ins   = conn.cursor()
            for p in preds:
                ins.execute("""
                    INSERT INTO predictions
                        (city, model, risk_level, risk_score, confidence, predicted_at)
                    VALUES
                        (%(city)s, %(model)s, %(risk_level)s,
                         %(risk_score)s, %(confidence)s, %(predicted_at)s)
                """, p)
                total += 1
            ins.close()

        cur.close(); conn.close()
        return jsonify({"status": "ok", "predictions_stored": total})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ── Predictions ───────────────────────────────────────────────────────────────
@api_bp.route("/predictions")
def predictions():
    city  = request.args.get("city")
    limit = int(request.args.get("limit", 50))
    conn  = get_db()
    cur   = conn.cursor(dictionary=True)
    if city:
        cur.execute("SELECT * FROM predictions WHERE city=%s ORDER BY predicted_at DESC LIMIT %s", (city, limit))
    else:
        cur.execute("SELECT * FROM predictions ORDER BY predicted_at DESC LIMIT %s", (limit,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(_serial(rows))


# ── Metrics ───────────────────────────────────────────────────────────────────
@api_bp.route("/metrics")
def metrics():
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM model_metrics ORDER BY trained_at DESC LIMIT 30")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(_serial(rows))


# ── Logs ──────────────────────────────────────────────────────────────────────
@api_bp.route("/logs")
def logs():
    limit = int(request.args.get("limit", 50))
    conn  = get_db()
    cur   = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM fetch_logs ORDER BY logged_at DESC LIMIT %s", (limit,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify(_serial(rows))
