"""
Database connection pool and schema initialization
"""
import os
import mysql.connector
from mysql.connector import pooling
from flask import current_app

_pool = None


def get_pool():
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="airquality_pool",
            pool_size=5,
            host=current_app.config["DB_HOST"],
            port=current_app.config["DB_PORT"],
            database=current_app.config["DB_NAME"],
            user=current_app.config["DB_USER"],
            password=current_app.config["DB_PASSWORD"],
            autocommit=True,
        )
    return _pool


def get_connection():
    return get_pool().get_connection()


def init_db():
    """Create all required tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS air_quality_readings (
            id              BIGINT AUTO_INCREMENT PRIMARY KEY,
            city            VARCHAR(100) NOT NULL,
            source          VARCHAR(50)  NOT NULL,
            aqi             FLOAT,
            pm25            FLOAT,
            pm10            FLOAT,
            o3              FLOAT,
            no2             FLOAT,
            so2             FLOAT,
            co              FLOAT,
            temperature     FLOAT,
            humidity        FLOAT,
            wind_speed      FLOAT,
            fetched_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_city_fetched (city, fetched_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS health_predictions (
            id              BIGINT AUTO_INCREMENT PRIMARY KEY,
            city            VARCHAR(100) NOT NULL,
            model_name      VARCHAR(100) NOT NULL,
            risk_level      VARCHAR(50)  NOT NULL,
            risk_score      FLOAT        NOT NULL,
            confidence      FLOAT,
            features_used   JSON,
            predicted_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_city_predicted (city, predicted_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS model_metrics (
            id              BIGINT AUTO_INCREMENT PRIMARY KEY,
            model_name      VARCHAR(100) NOT NULL,
            accuracy        FLOAT,
            precision_score FLOAT,
            recall_score    FLOAT,
            f1_score        FLOAT,
            mae             FLOAT,
            rmse            FLOAT,
            trained_at      DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fetch_logs (
            id          BIGINT AUTO_INCREMENT PRIMARY KEY,
            source      VARCHAR(50),
            city        VARCHAR(100),
            status      VARCHAR(20),
            message     TEXT,
            logged_at   DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    cursor.close()
    conn.close()
    print("[DB] Tables initialized successfully.")
