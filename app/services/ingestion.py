import logging
from flask import current_app
from app.models.database import get_db
from app.services import waqi, openweather, openaq

log = logging.getLogger(__name__)

INSERT_SQL = """
    INSERT INTO readings
        (city, country, latitude, longitude, source,
         aqi, pm25, pm10, o3, no2, so2, co,
         temperature, humidity, wind_speed, wind_direction, fetched_at)
    VALUES
        (%(city)s, %(country)s, %(latitude)s, %(longitude)s, %(source)s,
         %(aqi)s, %(pm25)s, %(pm10)s, %(o3)s, %(no2)s, %(so2)s, %(co)s,
         %(temperature)s, %(humidity)s, %(wind_speed)s, %(wind_direction)s, %(fetched_at)s)
"""

LOG_SQL = "INSERT INTO fetch_logs (city, source, status, message) VALUES (%s, %s, %s, %s)"


def run():
    cfg      = current_app.config
    cities   = cfg["CITIES"]
    conn     = get_db()
    cur      = conn.cursor()
    inserted = 0

    for city in cities:
        name = city["name"]
        lat  = city["lat"]
        lon  = city["lon"]

        sources = [
            ("WAQI",           waqi.fetch,        (cfg["WAQI_TOKEN"],      name, city.get("waqi"))),
            ("OpenWeatherMap", openweather.fetch,  (cfg["OPENWEATHER_KEY"], name, lat, lon)),
            ("OpenAQ",         openaq.fetch,       (cfg["OPENAQ_KEY"],      name, lat, lon)),
        ]

        for src_name, fn, args in sources:
            try:
                data = fn(*args)
                if data:
                    cur.execute(INSERT_SQL, data)
                    cur.execute(LOG_SQL, (name, src_name, "ok", ""))
                    inserted += 1
                    log.info("[Ingestion] %s / %s inserted", name, src_name)
                else:
                    cur.execute(LOG_SQL, (name, src_name, "no_data", "API returned nothing"))
            except Exception as e:
                cur.execute(LOG_SQL, (name, src_name, "error", str(e)))
                log.error("[Ingestion] %s / %s error: %s", name, src_name, e)

    cur.close()
    conn.close()
    return inserted
