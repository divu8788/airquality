import requests
import logging
from datetime import datetime

log = logging.getLogger(__name__)


def fetch(token, city_name, waqi_id=None):
    """Fetch air quality data from WAQI API."""

    slug = waqi_id if waqi_id else city_name
    url = f"https://api.waqi.info/feed/{slug}/?token={token}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "ok":
            log.warning("[WAQI] Invalid response for %s", city_name)
            return None

        payload = data.get("data", {})
        iaqi = payload.get("iaqi", {})
        city_info = payload.get("city", {})
        geo = city_info.get("geo") or []

        # Safe extraction of coordinates
        latitude = geo[0] if len(geo) > 0 else None
        longitude = geo[1] if len(geo) > 1 else None

        # Safe AQI conversion
        raw_aqi = payload.get("aqi")
        try:
            aqi = float(raw_aqi)
        except (TypeError, ValueError):
            aqi = None

        # Helper function to extract pollutant values
        def get_val(key):
            return (iaqi.get(key) or {}).get("v")

        return {
            "city": city_name,
            "location_name": city_info.get("name"),
            "latitude": latitude,
            "longitude": longitude,
            "source": "WAQI",
            "aqi": aqi,
            "pm25": get_val("pm25"),
            "pm10": get_val("pm10"),
            "o3": get_val("o3"),
            "no2": get_val("no2"),
            "so2": get_val("so2"),
            "co": get_val("co"),
            "temperature": get_val("t"),
            "humidity": get_val("h"),
            "wind_speed": get_val("w"),
            "wind_direction": None,
            "fetched_at": datetime.utcnow(),
        }

    except requests.exceptions.RequestException as e:
        log.error("[WAQI REQUEST ERROR] city=%s error=%s", city_name, e)
    except Exception as e:
        log.error("[WAQI UNKNOWN ERROR] city=%s error=%s", city_name, e)

    return None