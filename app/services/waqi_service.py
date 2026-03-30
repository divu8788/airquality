"""
WAQI (World Air Quality Index) API Service
https://aqicn.org/api/
"""
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

BASE_URL = "https://api.waqi.info"


def fetch_city_aqi(token: str, city_name: str, waqi_id: str = None) -> dict | None:
    """Fetch AQI data for a city from WAQI."""
    try:
        if waqi_id:
            url = f"{BASE_URL}/feed/{waqi_id}/?token={token}"
        else:
            url = f"{BASE_URL}/feed/{city_name}/?token={token}"

        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if data.get("status") != "ok":
            logger.warning(f"[WAQI] Non-ok status for {city_name}: {data.get('status')}")
            return None

        iaqi = data["data"].get("iaqi", {})

        return {
            "city":        city_name,
            "source":      "waqi",
            "aqi":         data["data"].get("aqi"),
            "pm25":        iaqi.get("pm25", {}).get("v"),
            "pm10":        iaqi.get("pm10", {}).get("v"),
            "o3":          iaqi.get("o3",   {}).get("v"),
            "no2":         iaqi.get("no2",  {}).get("v"),
            "so2":         iaqi.get("so2",  {}).get("v"),
            "co":          iaqi.get("co",   {}).get("v"),
            "temperature": iaqi.get("t",    {}).get("v"),
            "humidity":    iaqi.get("h",    {}).get("v"),
            "wind_speed":  iaqi.get("w",    {}).get("v"),
            "fetched_at":  datetime.utcnow(),
        }

    except Exception as e:
        logger.error(f"[WAQI] Error fetching {city_name}: {e}")
        return None
