# Air Quality Health Risk Prediction System

> **Module:** B9AI001 — Data Acquisition and Processing  
> **Programme:** MSc Artificial Intelligence  
> **Student:** Gipra (divu8788)  
> **Live Application:** http://4.235.112.189:8080

---

## Project Overview

This project implements a **real-time Air Quality Health Risk Prediction System** — a complete end-to-end data pipeline that:

1. **Collects** real-time environmental data from two public APIs every 15 minutes
2. **Preprocesses** and transforms raw sensor data into ML-ready features
3. **Stores** all data in a MySQL relational database on an Azure Virtual Machine
4. **Trains** three machine learning classifiers to predict health risk levels
5. **Serves** predictions and data through a Flask REST API with a live web dashboard
6. **Deploys** automatically via a GitHub Actions CI/CD pipeline

---

## Live System

| Component | URL |
|-----------|-----|
| Dashboard | http://4.235.112.189:8080 |
| API Health Check | http://4.235.112.189:8080/api/health |
| Latest Readings | http://4.235.112.189:8080/api/readings/latest |
| Latest Predictions | http://4.235.112.189:8080/api/predictions |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Data Sources                            │
│         WAQI API                OpenWeatherMap API          │
│   (AQI, PM2.5, PM10, O3)    (Weather + Air Pollution)       │
└──────────────────┬──────────────────────────────────────────┘
                   │  Fetched every 15 minutes via cron
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                 Preprocessing Pipeline                      │
│  Null Handling → Risk Labelling → Feature Engineering       │
│                → Normalisation                              │
└──────────────────┬──────────────────────────────────────────┘
                   │  Transformed records
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              MySQL Database (Azure VM)                      │
│   readings | predictions | model_metrics | fetch_logs       │
└──────────────────┬──────────────────────────────────────────┘
                   │  Training data
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                   ML Pipeline                               │
│     Random Forest | Gradient Boosting | XGBoost             │
│          Comparative performance evaluation                 │
└──────────────────┬──────────────────────────────────────────┘
                   │  Risk predictions + metrics
                   ▼
┌─────────────────────────────────────────────────────────────┐
│           Flask REST API + Live Dashboard                   │
│         http://4.235.112.189:8080                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
airquality/
│
├── run.py                          # Application entry point
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables (not in repo)
├── pytest.ini                      # Test configuration
│
├── config/
│   └── settings.py                 # All configuration (API keys, DB, cities)
│
├── app/
│   ├── __init__.py                 # Flask app factory (create_app)
│   │
│   ├── routes/
│   │   ├── api.py                  # REST API endpoints
│   │   └── main.py                 # Dashboard route
│   │
│   ├── services/
│   │   ├── ingestion.py            # Orchestrates data collection
│   │   ├── waqi.py                 # WAQI API client
│   │   └── openweather.py          # OpenWeatherMap API client
│   │
│   ├── ml/
│   │   └── predictor.py            # ML training and prediction
│   │
│   └── models/
│       └── database.py             # MySQL connection pool + schema
│
├── templates/
│   └── dashboard.html              # Live web dashboard (Chart.js)
│
├── scripts/
│   └── airquality.service          # systemd service file
│
└── tests/                          # pytest test suite
    ├── conftest.py                  # Shared fixtures
    ├── test_api_health.py           # Health endpoint tests
    ├── test_api_readings.py         # Readings endpoint tests
    ├── test_api_fetch.py            # Fetch endpoint tests
    ├── test_api_predictions.py      # Predictions endpoint tests
    ├── test_api_logs.py             # Logs and metrics tests
    ├── test_services_waqi.py        # WAQI service unit tests
    ├── test_services_openweather.py # OpenWeatherMap unit tests
    ├── test_ml_predictor.py         # ML predictor unit tests
    └── test_integration.py         # Integration test
```

---

## Data Sources

### 1. WAQI — World Air Quality Index
- **URL:** https://waqi.info/api
- **Data:** AQI, PM2.5, PM10, O3, NO2, SO2, CO, temperature, humidity
- **Coverage:** 12,000+ monitoring stations worldwide
- **Licence:** Free for non-commercial use with attribution
- **Rate limit:** 1,000 requests/day (we use ~96/day)

### 2. OpenWeatherMap Air Pollution API
- **URL:** https://openweathermap.org/api/air-pollution
- **Data:** PM2.5, PM10, O3, NO2, SO2, CO plus full weather data
- **Coverage:** Global via latitude/longitude coordinates
- **Licence:** Free tier — 60 calls/minute
- **Rate limit:** 1,000,000 calls/month (we use ~288/day)

### Cities Monitored
| City | Latitude | Longitude |
|------|----------|-----------|
| Dublin | 53.3498 | -6.2603 |
| London | 51.5074 | -0.1278 |
| New York | 40.7128 | -74.0060 |
| Beijing | 39.9042 | 116.4074 |
| Mumbai | 19.0760 | 72.8777 |

---

## Preprocessing and Transformations

Four transformation steps are applied to all raw API data before storage and ML training:

### T1 — Null Value Handling
APIs frequently omit pollutants not measured at a specific station. Missing values are filled with the **column median** — chosen over mean because median is robust to outliers in environmental sensor data.

```python
df[col] = df[col].fillna(df[col].median())
```

### T2 — AQI to Health Risk Labelling
Continuous AQI values (0–500) are mapped to categorical health risk levels using **US EPA breakpoints**. This creates the target variable for ML classification.

| AQI Range | Risk Level |
|-----------|------------|
| 0 – 50 | Good |
| 51 – 100 | Moderate |
| 101 – 150 | Unhealthy for Sensitive Groups |
| 151 – 200 | Unhealthy |
| 201 – 300 | Very Unhealthy |
| 301+ | Hazardous |

### T3 — Feature Engineering
Four new features derived from existing columns:

| Feature | Formula | Meaning |
|---------|---------|---------|
| `pm_ratio` | PM2.5 / PM10 | Fine particle dominance |
| `heat_index` | temperature × humidity / 100 | Perceived discomfort |
| `hour` | from timestamp | Rush hour patterns |
| `dayofweek` | from timestamp | Weekday vs weekend |

### T4 — Normalisation
**StandardScaler** applied before ML training — scales all features to zero mean and unit variance. Without this, AQI (0–500) would dominate CO (0–5) purely due to scale difference.

---

## Database Schema

```sql
-- Raw sensor readings from all APIs
CREATE TABLE readings (
    id             BIGINT AUTO_INCREMENT PRIMARY KEY,
    city           VARCHAR(100),
    country        VARCHAR(100),
    latitude       FLOAT,
    longitude      FLOAT,
    source         VARCHAR(50),     -- 'WAQI' or 'OpenWeatherMap'
    aqi            FLOAT,
    pm25           FLOAT,
    pm10           FLOAT,
    o3             FLOAT,
    no2            FLOAT,
    so2            FLOAT,
    co             FLOAT,
    temperature    FLOAT,
    humidity       FLOAT,
    wind_speed     FLOAT,
    wind_direction FLOAT,
    fetched_at     DATETIME
);

-- ML model predictions per city
CREATE TABLE predictions (
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    city         VARCHAR(100),
    model        VARCHAR(100),   -- 'RandomForest', 'GradientBoosting', 'XGBoost'
    risk_level   VARCHAR(100),
    risk_score   FLOAT,          -- 0 to 100
    confidence   FLOAT,          -- 0.0 to 1.0
    predicted_at DATETIME
);

-- ML model performance metrics
CREATE TABLE model_metrics (
    id         BIGINT AUTO_INCREMENT PRIMARY KEY,
    model      VARCHAR(100),
    accuracy   FLOAT,
    f1         FLOAT,
    precision_ FLOAT,
    recall     FLOAT,
    mae        FLOAT,
    rmse       FLOAT,
    rows_used  INT,
    trained_at DATETIME
);

-- API fetch history and error tracking
CREATE TABLE fetch_logs (
    id        BIGINT AUTO_INCREMENT PRIMARY KEY,
    city      VARCHAR(100),
    source    VARCHAR(50),
    status    VARCHAR(20),   -- 'ok', 'error', 'no_data'
    message   TEXT,
    logged_at DATETIME
);
```

---

## Machine Learning

Three classifiers trained and compared on the same dataset:

| Model | Algorithm | Library |
|-------|-----------|---------|
| Random Forest | Ensemble of 150 decision trees | scikit-learn |
| Gradient Boosting | Sequential boosting, 100 estimators | scikit-learn |
| XGBoost | Optimised gradient boosting | xgboost |

**Features used (14 total):**
AQI, PM2.5, PM10, O3, NO2, SO2, CO, temperature, humidity, wind speed, PM ratio, heat index, hour of day, day of week

**Target variable:** Health risk level (6 classes)

**Evaluation metrics:** Accuracy, F1 score, Precision, Recall, MAE, RMSE

---

## REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Service health check |
| GET | `/api/readings` | All readings (supports `?city=` and `?limit=`) |
| GET | `/api/readings/latest` | Latest reading per city |
| POST | `/api/fetch` | Trigger immediate data fetch from all APIs |
| POST | `/api/train` | Retrain all ML models on latest data |
| POST | `/api/predict` | Run ML inference for all cities |
| GET | `/api/predictions` | All stored predictions |
| GET | `/api/metrics` | ML model performance metrics |
| GET | `/api/logs` | Fetch logs (success/error history) |

---

## Automated Scheduling

Data collection runs automatically via Linux cron on the Azure VM:

```bash
# Fetch from both APIs for all 5 cities — every 15 minutes
*/15 * * * * curl -s -X POST http://localhost:8080/api/fetch

# Run ML predictions for all cities — every hour
0 * * * * curl -s -X POST http://localhost:8080/api/predict

# Retrain all ML models on latest data — every midnight
0 0 * * * curl -s -X POST http://localhost:8080/api/train
```

---

## Testing

**61 tests — all passing.** Test suite uses pytest with mocking (no real API calls or DB needed).

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api_health.py -v
pytest tests/test_integration.py -v
```

### Test Coverage

| File | Type | Tests | What it covers |
|------|------|-------|----------------|
| `test_api_health.py` | Unit | 5 | Health endpoint, 404, HTTP methods |
| `test_api_readings.py` | Unit | 8 | Readings, filters, field validation |
| `test_api_fetch.py` | Unit | 6 | Fetch endpoint, error handling |
| `test_api_predictions.py` | Unit | 7 | Predictions, risk levels, scores |
| `test_api_logs.py` | Unit | 7 | Logs, metrics, accuracy range |
| `test_services_waqi.py` | Unit | 7 | WAQI fetch, null AQI, errors |
| `test_services_openweather.py` | Unit | 8 | OWM fetch, temperature, PM2.5 |
| `test_ml_predictor.py` | Unit | 12 | AQI→risk mapping, score ranges |
| `test_integration.py` | Integration | 1 | POST /fetch → GET /readings full cycle |

---

## CI/CD Pipeline

Every push to `main` branch triggers automatic deployment:

```
git push origin main
        ↓
GitHub Actions starts
        ↓
SSH into Azure VM (4.235.112.189)
        ↓
Pull latest code
        ↓
Install dependencies
        ↓
Run 61 pytest tests
        ↓
✅ Tests pass → restart Flask app → live in ~90 seconds
❌ Tests fail → deployment stops → live app protected
```

---

## Local Development Setup

```bash
# Clone repository
git clone https://github.com/divu8788/airquality.git
cd airquality

# Create virtual environment
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env           # Edit with your credentials

# Run locally
python run.py
# → http://localhost:8080

# Run tests
pytest tests/ -v
```

---

## Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key
DEBUG=False

# Database
DB_HOST=localhost
DB_PORT=3306
DB_NAME=myappdb
DB_USER=your_db_user
DB_PASSWORD=your_db_password

# API Keys
WAQI_TOKEN=your_waqi_token
OPENWEATHER_KEY=your_openweathermap_key

# Scheduler
FETCH_INTERVAL_MIN=15
```

---

## Ethical Considerations

- **No personal data** is collected — all measurements are public environmental sensor readings from government-operated monitoring stations
- Both APIs are used **within free tier limits** and in accordance with their terms of service
- **API keys** are stored in environment variables, never committed to version control
- Data collection runs at maximum **96 requests/day per API** — well within stated rate limits
- All external libraries and APIs are fully **attributed** in the documentation

---

## Technology Stack

| Category | Technology | Version |
|----------|-----------|---------|
| Backend | Python Flask | 3.0.3 |
| Database | MySQL | 8.0 |
| ML | scikit-learn | 1.5.1 |
| ML | XGBoost | 2.1.1 |
| Data | pandas | 2.2.2 |
| Server | Gunicorn | 22.0.0 |
| Testing | pytest + pytest-flask | 9.0.3 |
| Cloud | Azure Ubuntu VM | 24.04 LTS |
| CI/CD | GitHub Actions | — |
| Frontend | Chart.js | 4.4.1 |

---

## Attributions

| Resource | Licence | Usage |
|----------|---------|-------|
| Flask | BSD-3-Clause | Web framework |
| scikit-learn | BSD-3-Clause | ML models and preprocessing |
| XGBoost | Apache 2.0 | Gradient boosting classifier |
| pandas | BSD-3-Clause | Data manipulation |
| numpy | BSD-3-Clause | Numerical computing |
| mysql-connector-python | GPL-2.0 | MySQL connectivity |
| requests | Apache 2.0 | HTTP API calls |
| Chart.js | MIT | Dashboard charts |
| WAQI API | Free non-commercial | Air quality data |
| OpenWeatherMap API | Free tier | Weather and pollution data |
| US EPA AQI Breakpoints | Public domain | Risk level classification |
| Microsoft Azure | Student subscription | VM hosting |
| GitHub Actions | Free tier | CI/CD automation |