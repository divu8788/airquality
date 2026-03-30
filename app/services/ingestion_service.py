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

def _insert_reading(conn, r):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO air_quality_readings
            (city,country,latitude,longitude,timestamp_utc,aqi,pm25,pm10,
             o3,no2,so2,co,temperature,humidity,wind_speed,wind_direction,source_api)
        VALUES
            (%(city)s,%(country)s,%(latitude)s,%(longitude)s,%(timestamp_utc)s,
             %(aqi)s,%(pm25)s,%(pm10)s,%(o3)s,%(no2)s,%(so2)s,%(co)s,
             %(temperature)s,%(humidity)s,%(wind_speed)s,%(wind_direction)s,%(source_api)s)
    """, r)
    cur.close()

def _log(conn, source, city, status, msg=""):
    cur = conn.cursor()
    cur.execute("INSERT INTO fetch_logs (source,city,status,message) VALUES (%s,%s,%s,%s)", (source,city,status,msg))
    cur.close()

# def fetch_and_store_all():
#     cities   = current_app.config["MONITORED_CITIES"]
#     conn     = get_connection()
#     inserted = 0
#     for city in cities:
#         name = city["name"]
#         for fn, src, args in [
#             (waqi_service.fetch_city_aqi,        "WAQI",           (current_app.config["WAQI_TOKEN"], name, city.get("waqi_id"))),
#             (openweather_service.fetch_city_data, "OpenWeatherMap", (current_app.config["OPENWEATHER_KEY"], name, city["lat"], city["lon"])),
#             (openaq_service.fetch_city_data,      "OpenAQ",         (current_app.config["OPENAQ_KEY"], name, city["lat"], city["lon"])),
#         ]:
#             reading = fn(*args)
#             if reading:
#                 _insert_reading(conn, reading)
#                 _log(conn, src, name, "success")
#                 inserted += 1
#             else:
#                 _log(conn, src, name, "error", "No data returned")
#     conn.close()
#     logger.info(f"[Ingestion] {inserted} records inserted")
#     return inserted

def fetch_and_store_all():
    cities   = current_app.config["MONITORED_CITIES"]
    conn     = get_connection()
    inserted = 0

    for city in cities:
        name = city["name"]

        for fn, src, args in [
            (waqi_service.fetch_city_aqi, "WAQI", (current_app.config["WAQI_TOKEN"], name, city.get("waqi_id"))),
            (openweather_service.fetch_city_data, "OpenWeatherMap", (current_app.config["OPENWEATHER_KEY"], name, city["lat"], city["lon"])),
            (openaq_service.fetch_city_data, "OpenAQ", (current_app.config["OPENAQ_KEY"], name, city["lat"], city["lon"])),
        ]:
            try:
                reading = fn(*args)

                if reading:
                    _insert_reading(conn, reading)
                    _log(conn, src, name, "success")
                    inserted += 1
                else:
                    _log(conn, src, name, "error", "No data returned")

            except Exception as e:
                print(f"[ERROR] {src} - {name}: {e}")
                _log(conn, src, name, "error", str(e))

    conn.close()
    print(f"[Ingestion] {inserted} records inserted")
    return inserted
PYEOF