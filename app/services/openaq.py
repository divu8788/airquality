# import requests
# import logging
# from datetime import datetime

# log = logging.getLogger(__name__)
# BASE = "https://api.openaq.org/v3"


# def fetch(api_key, city_name, lat, lon, radius=25000):
#     try:
#         headers = {"X-API-Key": api_key}
#         locs = requests.get(
#             BASE + "/locations?coordinates=" + str(lat) + "," + str(lon) +
#             "&radius=" + str(radius) + "&limit=5",
#             headers=headers, timeout=10
#         ).json().get("results", [])

#         if not locs:
#             log.warning("[OpenAQ] No locations near %s", city_name)
#             return None

#         bucket = {"pm25": [], "pm10": [], "o3": [], "no2": [], "so2": [], "co": []}
#         for loc in locs[:3]:
#             r = requests.get(
#                 BASE + "/locations/" + str(loc["id"]) + "/latest",
#                 headers=headers, timeout=10
#             )
#             if r.status_code != 200:
#                 continue
#             for s in r.json().get("results", []):
#                 param = s.get("parameter", {}).get("name", "").lower()
#                 val   = s.get("value")
#                 if param in bucket and val is not None:
#                     bucket[param].append(float(val))

#         def avg(lst):
#             return round(sum(lst) / len(lst), 2) if lst else None

#         pm25 = avg(bucket["pm25"])
#         aqi  = None
#         if pm25 is not None:
#             if pm25 <= 12:
#                 aqi = pm25 * 50 / 12
#             elif pm25 <= 35.4:
#                 aqi = 50 + (pm25 - 12) * 50 / 23.4
#             elif pm25 <= 55.4:
#                 aqi = 100 + (pm25 - 35.4) * 50 / 20
#             elif pm25 <= 150:
#                 aqi = 150 + (pm25 - 55.4) * 50 / 94.6
#             else:
#                 aqi = 200 + (pm25 - 150) * 100 / 100
#             aqi = round(aqi, 1)

#         return {
#             "city":          city_name,
#             "country":       None,
#             "latitude":      lat,
#             "longitude":     lon,
#             "source":        "OpenAQ",
#             "aqi":           aqi,
#             "pm25":          pm25,
#             "pm10":          avg(bucket["pm10"]),
#             "o3":            avg(bucket["o3"]),
#             "no2":           avg(bucket["no2"]),
#             "so2":           avg(bucket["so2"]),
#             "co":            avg(bucket["co"]),
#             "temperature":   None,
#             "humidity":      None,
#             "wind_speed":    None,
#             "wind_direction": None,
#             "fetched_at":    datetime.utcnow(),
#         }
#     except Exception as e:
#         log.error("[OpenAQ] %s: %s", city_name, e)
#         return None
