# Air Quality Health Risk Prediction System

Real-time air quality monitoring and ML-powered health risk prediction using
**WAQI**, **OpenWeatherMap**, and **OpenAQ** APIs, backed by **MySQL** and served
via **Flask** on an **Azure VM**.

---

## Project Structure

```
airquality/
├── run.py                          # App entry point
├── requirements.txt
├── .env                            # ← never commit this
├── .gitignore
├── config/
│   └── settings.py                 # All config & env vars
├── app/
│   ├── __init__.py                 # Flask app factory
│   ├── models/
│   │   └── database.py             # DB pool + schema init
│   ├── services/
│   │   ├── waqi_service.py         # WAQI API client
│   │   ├── openweather_service.py  # OpenWeatherMap client
│   │   ├── openaq_service.py       # OpenAQ v3 client
│   │   ├── ingestion_service.py    # Orchestrates all fetches
│   │   ├── prediction_service.py   # Stores ML predictions
│   │   └── training_service.py     # Pulls data, retrains models
│   ├── ml/
│   │   └── predictor.py            # RandomForest, GBM, XGBoost
│   └── routes/
│       ├── api.py                  # REST endpoints
│       ├── predictions.py          # Prediction endpoints
│       └── dashboard.py            # Dashboard HTML
├── scheduler/
│   └── jobs.py                     # APScheduler jobs
├── templates/
│   └── dashboard.html              # Live dashboard UI
├── nginx/
│   └── airquality.conf             # Nginx reverse proxy
└── scripts/
    ├── airquality.service          # systemd service file
    └── vm_setup.sh                 # One-shot VM provisioning
```

---

## Step 1 — Local Development Setup

```bash
# Clone your repo
git clone https://github.com/YOUR_USERNAME/airquality.git
cd airquality

# Create virtual environment
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and edit environment file
cp .env .env.local   # keep .env.local for reference; edit .env

# Run locally
python run.py
# → http://localhost:8080
```

---

## Step 2 — Push to GitHub

```bash
git init                          # (if not already a git repo)
git add .
git commit -m "Initial commit — Air Quality Prediction System"

# Create repo on github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/airquality.git
git branch -M main
git push -u origin main
```

---

## Step 3 — Configure GitHub Secrets for CI/CD

In your GitHub repo → **Settings → Secrets → Actions**, add:

| Secret Name  | Value                                      |
|--------------|--------------------------------------------|
| `VM_HOST`    | `4.235.112.189`                            |
| `VM_USER`    | `azureuser`                                |
| `VM_SSH_KEY` | Contents of your Azure VM private key file |

Generate an SSH key pair if needed:
```bash
ssh-keygen -t ed25519 -C "github-deploy" -f ~/.ssh/github_deploy
# Add ~/.ssh/github_deploy.pub to VM's ~/.ssh/authorized_keys
# Paste contents of ~/.ssh/github_deploy as VM_SSH_KEY secret
```

---

## Step 4 — Azure VM Setup

SSH into your VM and run the setup script:

```bash
ssh azureuser@4.235.112.189
# Upload setup script or clone repo first, then:
bash scripts/vm_setup.sh
```

### Open port 8080 in Azure Portal
1. Go to your VM → **Networking** → **Add inbound port rule**
2. Destination port: **8080**, Protocol: TCP, Action: Allow

---

## Step 5 — Verify Deployment

```bash
# Check service status
sudo systemctl status airquality

# Watch live logs
journalctl -u airquality -f

# Test API endpoints
curl http://4.235.112.189/api/health
curl http://4.235.112.189/api/readings/latest
```

---

## Step 6 — Using the System

### Dashboard
Visit: `http://4.235.112.189:8080`  
(or port 80 if Nginx is configured)

### Manual API Calls

| Endpoint                    | Method | Description                        |
|-----------------------------|--------|------------------------------------|
| `/api/health`               | GET    | Health check                       |
| `/api/readings`             | GET    | All readings (latest 100)          |
| `/api/readings/latest`      | GET    | Latest reading per city            |
| `/api/fetch`                | POST   | Trigger immediate data fetch       |
| `/api/train`                | POST   | Retrain all ML models              |
| `/api/predictions/`         | GET    | All predictions                    |
| `/api/predictions/latest`   | GET    | Latest prediction per city         |
| `/api/predictions/run`      | POST   | Run predictions now                |
| `/api/model-metrics`        | GET    | ML model performance metrics       |
| `/api/logs`                 | GET    | Fetch logs (success/error)         |

---

## Scheduler Jobs (Automatic)

| Job               | Frequency     | Description                            |
|-------------------|---------------|----------------------------------------|
| `fetch_data`      | Every 15 min  | Fetch from WAQI + OWM + OpenAQ         |
| `run_predictions` | Every hour    | Run ML inference, store predictions    |
| `retrain_models`  | Every 24 hrs  | Retrain with latest accumulated data  |

---

## ML Models Compared

| Model             | Type             | Library       |
|-------------------|------------------|---------------|
| Random Forest     | Ensemble         | scikit-learn  |
| Gradient Boosting | Ensemble         | scikit-learn  |
| XGBoost           | Gradient Boosting| xgboost       |

**Risk Categories:**
- 🟢 Good (AQI 0–50)
- 🟡 Moderate (51–100)
- 🟠 Unhealthy for Sensitive Groups (101–150)
- 🔴 Unhealthy (151–200)
- 🟣 Very Unhealthy (201–300)
- ⚫ Hazardous (301+)

---

## Auto-Deploy Flow

```
git push origin main
      ↓
GitHub Actions triggers deploy.yml
      ↓
SSH into Azure VM (4.235.112.189)
      ↓
git pull + pip install + systemctl restart airquality
      ↓
Live in ~30 seconds
```

---

## Troubleshooting

```bash
# App won't start
journalctl -u airquality -n 50

# DB connection error
mysql -u myappGipra -p myappdb      # test connection manually

# Port 8080 not accessible
sudo ufw allow 8080/tcp             # open firewall
# AND add Azure inbound rule for port 8080

# API key errors
# Check .env file exists on VM and has correct values
cat /home/azureuser/airquality/.env
```
# trigger deploy
# test deploy
fix ssh
fix ssh
