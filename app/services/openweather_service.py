import requests, logging
from datetime import datetime
logger = logging.getLogger(__name__)

def fetch_city_data(api_key, city_name, lat, lon):
    try:
        ap = requests.get(f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}", timeout=10).json()
        wx = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric", timeout=10).json()
        comp = ap["list"][0]["components"]
        return {
            "city": city_name,
            "country": wx.get("sys",{}).get("country"),
            "latitude": lat, "longitude": lon,
            "timestamp_utc": datetime.utcnow(),
            "aqi": ap["list"][0]["main"]["aqi"] * 50,
            "pm25": comp.get("pm2_5"), "pm10": comp.get("pm10"),
            "o3":   comp.get("o3"),    "no2":  comp.get("no2"),
            "so2":  comp.get("so2"),   "co":   comp.get("co"),
            "temperature":    wx["main"].get("temp"),
            "humidity":       wx["main"].get("humidity"),
            "wind_speed":     wx["wind"].get("speed"),
            "wind_direction": wx["wind"].get("deg"),
            "source_api":     "OpenWeatherMap",
        }
    except Exception as e:
        logger.error(f"[OWM] {city_name}: {e}")
        return None
PYEOF