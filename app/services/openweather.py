import requests
import logging
from datetime import datetime

log = logging.getLogger(__name__)


def fetch(api_key, city_name, lat, lon):
    try:
        ap = requests.get(
            "http://api.openweathermap.org/data/2.5/air_pollution"
            "?lat=" + str(lat) + "&lon=" + str(lon) + "&appid=" + api_key,
            timeout=10
        ).json()
        wx = requests.get(
            "https://api.openweathermap.org/data/2.5/weather"
            "?lat=" + str(lat) + "&lon=" + str(lon) + "&appid=" + api_key + "&units=metric",
            timeout=10
        ).json()
        comp = ap["list"][0]["components"]
        return {
            "city":          city_name,
            "country":       wx.get("sys", {}).get("country"),
            "latitude":      lat,
            "longitude":     lon,
            "source":        "OpenWeatherMap",
            "aqi":           ap["list"][0]["main"]["aqi"] * 50,
            "pm25":          comp.get("pm2_5"),
            "pm10":          comp.get("pm10"),
            "o3":            comp.get("o3"),
            "no2":           comp.get("no2"),
            "so2":           comp.get("so2"),
            "co":            comp.get("co"),
            "temperature":   wx["main"].get("temp"),
            "humidity":      wx["main"].get("humidity"),
            "wind_speed":    wx["wind"].get("speed"),
            "wind_direction": wx["wind"].get("deg"),
            "fetched_at":    datetime.utcnow(),
        }
    except Exception as e:
        log.error("[OWM] %s: %s", city_name, e)
        return None
