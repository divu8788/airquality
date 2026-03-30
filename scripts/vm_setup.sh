#!/bin/bash
# ============================================================
# Azure VM Setup Script
# Run once as azureuser on your Ubuntu VM
# Usage: bash scripts/vm_setup.sh
# ============================================================
set -e

echo "=== [1/8] Updating system packages ==="
sudo apt-get update -y && sudo apt-get upgrade -y

echo "=== [2/8] Installing Python, Nginx, Git ==="
sudo apt-get install -y python3 python3-pip python3-venv git nginx

echo "=== [3/8] Cloning repository ==="
# Replace with your actual GitHub repo URL
REPO_URL="https://github.com/YOUR_USERNAME/airquality.git"
APP_DIR="/home/azureuser/airquality"

if [ ! -d "$APP_DIR" ]; then
  git clone "$REPO_URL" "$APP_DIR"
else
  echo "Directory exists — skipping clone."
fi
cd "$APP_DIR"

echo "=== [4/8] Creating Python virtual environment ==="
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "=== [5/8] Creating .env file ==="
cat > "$APP_DIR/.env" << 'EOF'
SECRET_KEY=CHANGE-THIS-TO-RANDOM-64-CHAR-STRING
DEBUG=False

DB_HOST=localhost
DB_PORT=3306
DB_NAME=myappdb
DB_USER=myappGipra
DB_PASSWORD=Gipra@8788!

WAQI_TOKEN=9262e0b716c45f1cc173d16f8f11ba318031753c
OPENWEATHER_KEY=82fe5f765a5af310a7e8bb877ebe0970
OPENAQ_KEY=aefea848f4587472652a798c229d7e14926e35267a78dc95fd8cc7b013d34cd0

FETCH_INTERVAL_MINUTES=15
EOF
echo "⚠️  Edit .env to verify your credentials!"

echo "=== [6/8] Setting up log directory ==="
sudo mkdir -p /var/log/airquality
sudo chown azureuser:azureuser /var/log/airquality

echo "=== [7/8] Installing systemd service ==="
sudo cp "$APP_DIR/scripts/airquality.service" /etc/systemd/system/airquality.service
sudo systemctl daemon-reload
sudo systemctl enable airquality
sudo systemctl start airquality
echo "Service status:"
sudo systemctl status airquality --no-pager

echo "=== [8/8] Configuring Nginx ==="
sudo cp "$APP_DIR/nginx/airquality.conf" /etc/nginx/sites-available/airquality
sudo ln -sf /etc/nginx/sites-available/airquality /etc/nginx/sites-enabled/airquality
sudo nginx -t && sudo systemctl reload nginx

echo ""
echo "✅ Setup complete!"
echo "   App running at: http://4.235.112.189"
echo "   API health:     http://4.235.112.189/api/health"
echo "   Logs:           journalctl -u airquality -f"
