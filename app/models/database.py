import mysql.connector
from mysql.connector import pooling
from flask import current_app

_pool = None


def get_pool():
    global _pool
    if _pool is None:
        cfg = current_app.config
        _pool = pooling.MySQLConnectionPool(
            pool_name="aqpool",
            pool_size=5,
            autocommit=True,
            host=cfg["DB_HOST"],
            port=cfg["DB_PORT"],
            database=cfg["DB_NAME"],
            user=cfg["DB_USER"],
            password=cfg["DB_PASSWORD"],
        )
    return _pool


def get_db():
    return get_pool().get_connection()


def init_db():
    conn = get_db()
    cur  = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id             BIGINT AUTO_INCREMENT PRIMARY KEY,
            city           VARCHAR(100) NOT NULL,
            country        VARCHAR(100),
            latitude       FLOAT,
            longitude      FLOAT,
            source         VARCHAR(50)  NOT NULL,
            aqi            FLOAT,
            pm25           FLOAT,
            pm10           FLOAT,
            o3             FLOAT,
            no2            FLOAT,
            so2            FLOAT,
            co             FLOAT,
            temperature    FLOAT,
            humidity       FLOAT,
            wind_speed     FLOAT,
            wind_direction FLOAT,
            fetched_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_city_time (city, fetched_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id           BIGINT AUTO_INCREMENT PRIMARY KEY,
            city         VARCHAR(100) NOT NULL,
            model        VARCHAR(100) NOT NULL,
            risk_level   VARCHAR(100) NOT NULL,
            risk_score   FLOAT        NOT NULL,
            confidence   FLOAT,
            predicted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_city_pred (city, predicted_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS model_metrics (
            id         BIGINT AUTO_INCREMENT PRIMARY KEY,
            model      VARCHAR(100) NOT NULL,
            accuracy   FLOAT,
            f1         FLOAT,
            precision_ FLOAT,
            recall     FLOAT,
            mae        FLOAT,
            rmse       FLOAT,
            rows_used  INT,
            trained_at DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS fetch_logs (
            id        BIGINT AUTO_INCREMENT PRIMARY KEY,
            city      VARCHAR(100),
            source    VARCHAR(50),
            status    VARCHAR(20),
            message   TEXT,
            logged_at DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    cur.close()
    conn.close()
    print("[DB] Tables ready.")
