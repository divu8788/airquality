import os
from dotenv import load_dotenv
load_dotenv()


class Config:
    SECRET_KEY         = os.getenv("SECRET_KEY",        "aq-secret-2024")
    DEBUG              = False
    DB_HOST            = os.getenv("DB_HOST",            "localhost")
    DB_PORT            = int(os.getenv("DB_PORT",        3306))
    DB_NAME            = os.getenv("DB_NAME",            "myappdb")
    DB_USER            = os.getenv("DB_USER",            "myappGipra")
    DB_PASSWORD        = os.getenv("DB_PASSWORD",        "Gipra@8788!")
    WAQI_TOKEN         = os.getenv("WAQI_TOKEN",         "9262e0b716c45f1cc173d16f8f11ba318031753c")
    OPENWEATHER_KEY    = os.getenv("OPENWEATHER_KEY",    "82fe5f765a5af310a7e8bb877ebe0970")
    OPENAQ_KEY         = os.getenv("OPENAQ_KEY",         "aefea848f4587472652a798c229d7e14926e35267a78dc95fd8cc7b013d34cd0")
    FETCH_INTERVAL_MIN = int(os.getenv("FETCH_INTERVAL_MIN", 15))

    CITIES = [
        {"name": "Dublin",   "lat": 53.3498, "lon": -6.2603,  "waqi": "dublin"},
        {"name": "London",   "lat": 51.5074, "lon": -0.1278,  "waqi": "london"},
        {"name": "New York", "lat": 40.7128, "lon": -74.0060, "waqi": "new-york"},
        {"name": "Beijing",  "lat": 39.9042, "lon": 116.4074, "waqi": "beijing"},
        {"name": "Mumbai",   "lat": 19.0760, "lon": 72.8777,  "waqi": "mumbai"},
    ]