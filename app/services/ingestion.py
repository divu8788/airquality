import logging
from flask import current_app
from app.models.database import get_db
from app.services import waqi, openweather

log = logging.getLogger(__name__)

INSERT_SQL = (
    "INSERT INTO readings "
    "(city, country, latitude, longitude, source, "
    " aqi, pm25, pm10, o3, no2, so2, co, "
    " temperature, humidity, wind_speed, wind_direction, fetched_at) "
    "VALUES "
    "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
)

LOG_SQL = "INSERT INTO fetch_logs (city, source, status, message) VALUES (%s, %s, %s, %s)"


def run():
    cfg      = current_app.config
    conn     = get_db()
    cur      = conn.cursor()
    inserted = 0

    for city in cfg["CITIES"]:
        name = city["name"]
        lat  = city["lat"]
        lon  = city["lon"]

        sources = [
            ("WAQI",           waqi.fetch,       (cfg["WAQI_TOKEN"],      name, city.get("waqi"))),
            ("OpenWeatherMap", openweather.fetch, (cfg["OPENWEATHER_KEY"], name, lat, lon)),
        ]

        for src_name, fn, args in sources:
            try:
                d = fn(*args)
                if d:
                    cur.execute(INSERT_SQL, (
                        d.get("city"),
                        d.get("country"),
                        d.get("latitude"),
                        d.get("longitude"),
                        d.get("source"),
                        d.get("aqi"),
                        d.get("pm25"),
                        d.get("pm10"),
                        d.get("o3"),
                        d.get("no2"),
                        d.get("so2"),
                        d.get("co"),
                        d.get("temperature"),
                        d.get("humidity"),
                        d.get("wind_speed"),
                        d.get("wind_direction"),
                        d.get("fetched_at"),
                    ))
                    cur.execute(LOG_SQL, (name, src_name, "ok", ""))
                    inserted += 1
                    log.info("[Ingestion] %s / %s OK", name, src_name)
                else:
                    cur.execute(LOG_SQL, (name, src_name, "no_data", "API returned nothing"))
            except Exception as e:
                cur.execute(LOG_SQL, (name, src_name, "error", str(e)))
                log.error("[Ingestion] %s / %s error: %s", name, src_name, e)

    cur.close()
    conn.close()
    return inserted
