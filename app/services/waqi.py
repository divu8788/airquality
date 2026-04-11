import requests
import logging
from datetime import datetime

log = logging.getLogger(__name__)


def fetch(token, city_name, waqi_id=None):
    """Fetch air quality data from WAQI API."""
    try:
        slug = waqi_id if waqi_id else city_name
        url  = "https://api.waqi.info/feed/" + slug + "/?token=" + token
        r    = requests.get(url, timeout=10)
        r.raise_for_status()
        d = r.json()

        if d.get("status") != "ok":
            log.warning("[WAQI] Non-ok status for %s: %s", city_name, d.get("status"))
            return None

        iaqi = d["data"].get("iaqi", {})
        geo  = d["data"].get("city", {}).get("geo") or [None, None]

        # AQI can be "-" for inactive stations — handle safely
        try:
            aqi = float(d["data"].get("aqi"))
        except (TypeError, ValueError):
            aqi = None

        return {
            "city":           city_name,
            "country":        d["data"].get("city", {}).get("name"),
            "latitude":       geo[0] if geo else None,
            "longitude":      geo[1] if geo else None,
            "source":         "WAQI",
            "aqi":            aqi,
            "pm25":           (iaqi.get("pm25") or {}).get("v"),
            "pm10":           (iaqi.get("pm10") or {}).get("v"),
            "o3":             (iaqi.get("o3")   or {}).get("v"),
            "no2":            (iaqi.get("no2")  or {}).get("v"),
            "so2":            (iaqi.get("so2")  or {}).get("v"),
            "co":             (iaqi.get("co")   or {}).get("v"),
            "temperature":    (iaqi.get("t")    or {}).get("v"),
            "humidity":       (iaqi.get("h")    or {}).get("v"),
            "wind_speed":     (iaqi.get("w")    or {}).get("v"),
            "wind_direction": None,
            "fetched_at":     datetime.utcnow(),
        }

    except Exception as e:
        log.error("[WAQI] %s: %s", city_name, e)
        return None
