import os
from dotenv import load_dotenv
load_dotenv()


class Config:
    SECRET_KEY          = os.getenv("SECRET_KEY", "change-me")
    DEBUG               = False
    DB_HOST             = os.getenv("DB_HOST",     "localhost")
    DB_PORT             = int(os.getenv("DB_PORT", 3306))
    DB_NAME             = os.getenv("DB_NAME",     "myappdb")
    DB_USER             = os.getenv("DB_USER",     "myappGipra")
    DB_PASSWORD         = os.getenv("DB_PASSWORD")
    WAQI_TOKEN          = os.getenv("WAQI_TOKEN")
    OPENWEATHER_KEY     = os.getenv("OPENWEATHER_KEY")
    OPENAQ_KEY          = os.getenv("OPENAQ_KEY")
    FETCH_INTERVAL_MIN  = int(os.getenv("FETCH_INTERVAL_MIN", 15))

    CITIES = [
        {"name": "Dublin",   "lat": 53.3498, "lon": -6.2603,  "waqi": "dublin"},
        {"name": "London",   "lat": 51.5074, "lon": -0.1278,  "waqi": "london"},
        {"name": "New York", "lat": 40.7128, "lon": -74.0060, "waqi": "new-york"},
        {"name": "Beijing",  "lat": 39.9042, "lon": 116.4074, "waqi": "beijing"},
        {"name": "Mumbai",   "lat": 19.0760, "lon": 72.8777,  "waqi": "mumbai"},
    ]