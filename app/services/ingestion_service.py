"""
Data Ingestion Service
Orchestrates fetching from all three APIs and persisting to MySQL.
"""
import logging
from datetime import datetime
from flask import current_app
from app.models.database import get_connection
from app.services import waqi_service, openweather_service, openaq_service

logger = logging.getLogger(__name__)


def _insert_reading(conn, reading: dict):
    cursor = conn.cursor()
    sql = """
        INSERT INTO air_quality_readings
            (city, source, aqi, pm25, pm10, o3, no2, so2, co,
             temperature, humidity, wind_speed, fetched_at)
        VALUES
            (%(city)s, %(source)s, %(aqi)s, %(pm25)s, %(pm10)s,
             %(o3)s, %(no2)s, %(so2)s, %(co)s,
             %(temperature)s, %(humidity)s, %(wind_speed)s, %(fetched_at)s)
    """
    cursor.execute(sql, reading)
    cursor.close()


def _log_fetch(conn, source, city, status, message=""):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO fetch_logs (source, city, status, message) VALUES (%s, %s, %s, %s)",
        (source, city, status, message)
    )
    cursor.close()


def fetch_and_store_all():
    """Main ingestion job called by the scheduler."""
    cities = current_app.config["MONITORED_CITIES"]
    waqi_token = current_app.config["WAQI_TOKEN"]
    owm_key = current_app.config["OPENWEATHER_KEY"]
    openaq_key = current_app.config["OPENAQ_KEY"]

    conn = get_connection()
    total_inserted = 0

    for city in cities:
        name = city["name"]
        lat  = city["lat"]
        lon  = city["lon"]

        # --- WAQI ---
        reading = waqi_service.fetch_city_aqi(waqi_token, name, city.get("waqi_id"))
        if reading:
            _insert_reading(conn, reading)
            _log_fetch(conn, "waqi", name, "success")
            total_inserted += 1
        else:
            _log_fetch(conn, "waqi", name, "error", "No data returned")

        # --- OpenWeatherMap ---
        reading = openweather_service.fetch_city_data(owm_key, name, lat, lon)
        if reading:
            _insert_reading(conn, reading)
            _log_fetch(conn, "openweathermap", name, "success")
            total_inserted += 1
        else:
            _log_fetch(conn, "openweathermap", name, "error", "No data returned")

        # --- OpenAQ ---
        reading = openaq_service.fetch_city_data(openaq_key, name, lat, lon)
        if reading:
            _insert_reading(conn, reading)
            _log_fetch(conn, "openaq", name, "success")
            total_inserted += 1
        else:
            _log_fetch(conn, "openaq", name, "error", "No data returned")

    conn.close()
    logger.info(f"[Ingestion] Completed — {total_inserted} records inserted at {datetime.utcnow()}")
    return total_inserted
