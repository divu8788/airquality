"""
OpenWeatherMap Air Pollution + Weather API Service
https://openweathermap.org/api/air-pollution
"""
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

AQI_LABELS = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}


def fetch_city_data(api_key: str, city_name: str, lat: float, lon: float) -> dict | None:
    """Fetch air pollution + weather data for a lat/lon from OpenWeatherMap."""
    try:
        # Air pollution endpoint
        ap_url = (
            f"http://api.openweathermap.org/data/2.5/air_pollution"
            f"?lat={lat}&lon={lon}&appid={api_key}"
        )
        ap_resp = requests.get(ap_url, timeout=10)
        ap_resp.raise_for_status()
        ap_data = ap_resp.json()

        # Current weather for temperature/humidity/wind
        wx_url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        )
        wx_resp = requests.get(wx_url, timeout=10)
        wx_resp.raise_for_status()
        wx_data = wx_resp.json()

        comp = ap_data["list"][0]["components"]
        aqi_index = ap_data["list"][0]["main"]["aqi"]

        return {
            "city":        city_name,
            "source":      "openweathermap",
            "aqi":         aqi_index * 50,          # scale 1-5 → approximate AQI
            "pm25":        comp.get("pm2_5"),
            "pm10":        comp.get("pm10"),
            "o3":          comp.get("o3"),
            "no2":         comp.get("no2"),
            "so2":         comp.get("so2"),
            "co":          comp.get("co"),
            "temperature": wx_data["main"].get("temp"),
            "humidity":    wx_data["main"].get("humidity"),
            "wind_speed":  wx_data["wind"].get("speed"),
            "fetched_at":  datetime.utcnow(),
        }

    except Exception as e:
        logger.error(f"[OWM] Error fetching {city_name}: {e}")
        return None
