"""
Air Quality Health Risk Prediction System
Entry point for Flask application
"""
from app import create_app
from scheduler.jobs import start_scheduler

app = create_app()

if __name__ == "__main__":
    start_scheduler(app)
    app.run(host="0.0.0.0", port=8080, debug=True)
