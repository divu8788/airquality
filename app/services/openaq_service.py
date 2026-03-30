"""
OpenAQ API v3 Service
https://docs.openaq.org/
"""
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

BASE_URL = "https://api.openaq.org/v3"


def fetch_city_data(api_key: str, city_name: str, lat: float, lon: float, radius: int = 25000) -> dict | None:
    """
    Fetch latest measurements near a lat/lon from OpenAQ.
    Returns averaged values across nearby stations.
    """
    try:
        headers = {"X-API-Key": api_key}

        # Find locations near the city
        loc_url = f"{BASE_URL}/locations?coordinates={lat},{lon}&radius={radius}&limit=5"
        loc_resp = requests.get(loc_url, headers=headers, timeout=10)
        loc_resp.raise_for_status()
        locations = loc_resp.json().get("results", [])

        if not locations:
            logger.warning(f"[OpenAQ] No locations found near {city_name}")
            return None

        # Collect parameter values across stations
        measurements = {"pm25": [], "pm10": [], "o3": [], "no2": [], "so2": [], "co": []}
        param_map = {"pm25": "pm25", "pm10": "pm10", "o3": "o3", "no2": "no2", "so2": "so2", "co": "co"}

        for loc in locations[:3]:
            loc_id = loc["id"]
            meas_url = f"{BASE_URL}/locations/{loc_id}/latest"
            meas_resp = requests.get(meas_url, headers=headers, timeout=10)
            if meas_resp.status_code != 200:
                continue
            for sensor in meas_resp.json().get("results", []):
                param = sensor.get("parameter", {}).get("name", "").lower()
                value = sensor.get("value")
                if param in measurements and value is not None:
                    measurements[param].append(float(value))

        def avg(lst):
            return round(sum(lst) / len(lst), 2) if lst else None

        pm25_val = avg(measurements["pm25"])

        # Estimate AQI from PM2.5 using US EPA breakpoints (simplified)
        aqi_est = None
        if pm25_val is not None:
            if pm25_val <= 12:    aqi_est = pm25_val * 50 / 12
            elif pm25_val <= 35.4: aqi_est = 50 + (pm25_val - 12) * 50 / 23.4
            elif pm25_val <= 55.4: aqi_est = 100 + (pm25_val - 35.4) * 50 / 20
            elif pm25_val <= 150:  aqi_est = 150 + (pm25_val - 55.4) * 50 / 94.6
            else:                  aqi_est = 200 + (pm25_val - 150) * 100 / 100
            aqi_est = round(aqi_est, 1)

        return {
            "city":        city_name,
            "source":      "openaq",
            "aqi":         aqi_est,
            "pm25":        pm25_val,
            "pm10":        avg(measurements["pm10"]),
            "o3":          avg(measurements["o3"]),
            "no2":         avg(measurements["no2"]),
            "so2":         avg(measurements["so2"]),
            "co":          avg(measurements["co"]),
            "temperature": None,   # OpenAQ does not provide weather
            "humidity":    None,
            "wind_speed":  None,
            "fetched_at":  datetime.utcnow(),
        }

    except Exception as e:
        logger.error(f"[OpenAQ] Error fetching {city_name}: {e}")
        return None
