import requests, logging
from datetime import datetime
logger = logging.getLogger(__name__)
BASE_URL = "https://api.waqi.info"

def fetch_city_aqi(token, city_name, waqi_id=None):
    try:
        url  = f"{BASE_URL}/feed/{waqi_id or city_name}/?token={token}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") != "ok":
            return None
        iaqi = data["data"].get("iaqi", {})
        geo  = data["data"].get("city", {}).get("geo", [None, None])
        return {
            "city": city_name,
            "country": data["data"].get("city", {}).get("name"),
            "latitude": geo[0] if geo else None,
            "longitude": geo[1] if geo else None,
            "timestamp_utc": datetime.utcnow(),
            "aqi": data["data"].get("aqi"),
            "pm25": iaqi.get("pm25",{}).get("v"),
            "pm10": iaqi.get("pm10",{}).get("v"),
            "o3":   iaqi.get("o3",{}).get("v"),
            "no2":  iaqi.get("no2",{}).get("v"),
            "so2":  iaqi.get("so2",{}).get("v"),
            "co":   iaqi.get("co",{}).get("v"),
            "temperature":    iaqi.get("t",{}).get("v"),
            "humidity":       iaqi.get("h",{}).get("v"),
            "wind_speed":     iaqi.get("w",{}).get("v"),
            "wind_direction": None,
            "source_api":     "WAQI",
        }
    except Exception as e:
        logger.error(f"[WAQI] {city_name}: {e}")
        return None
PYEOF