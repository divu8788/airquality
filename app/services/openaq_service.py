import requests, logging
from datetime import datetime
logger = logging.getLogger(__name__)
BASE_URL = "https://api.openaq.org/v3"

def fetch_city_data(api_key, city_name, lat, lon, radius=25000):
    try:
        headers  = {"X-API-Key": api_key}
        locs     = requests.get(f"{BASE_URL}/locations?coordinates={lat},{lon}&radius={radius}&limit=5", headers=headers, timeout=10).json().get("results", [])
        if not locs:
            return None
        meas = {"pm25":[],"pm10":[],"o3":[],"no2":[],"so2":[],"co":[]}
        for loc in locs[:3]:
            r = requests.get(f"{BASE_URL}/locations/{loc['id']}/latest", headers=headers, timeout=10)
            if r.status_code != 200: continue
            for s in r.json().get("results", []):
                p = s.get("parameter",{}).get("name","").lower()
                v = s.get("value")
                if p in meas and v is not None:
                    meas[p].append(float(v))
        def avg(l): return round(sum(l)/len(l),2) if l else None
        pm25 = avg(meas["pm25"])
        aqi  = None
        if pm25:
            if pm25<=12: aqi=pm25*50/12
            elif pm25<=35.4: aqi=50+(pm25-12)*50/23.4
            elif pm25<=55.4: aqi=100+(pm25-35.4)*50/20
            elif pm25<=150:  aqi=150+(pm25-55.4)*50/94.6
            else:            aqi=200+(pm25-150)*100/100
            aqi=round(aqi,1)
        return {
            "city": city_name, "country": None,
            "latitude": lat, "longitude": lon,
            "timestamp_utc": datetime.utcnow(),
            "aqi": aqi, "pm25": pm25,
            "pm10": avg(meas["pm10"]), "o3": avg(meas["o3"]),
            "no2": avg(meas["no2"]),   "so2": avg(meas["so2"]),
            "co": avg(meas["co"]),
            "temperature": None, "humidity": None,
            "wind_speed": None,  "wind_direction": None,
            "source_api": "OpenAQ",
        }
    except Exception as e:
        logger.error(f"[OpenAQ] {city_name}: {e}")
        return None
PYEOF