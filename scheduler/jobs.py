import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

log = logging.getLogger(__name__)


def start_scheduler(app):
    s = BackgroundScheduler(daemon=True)

    def fetch_job():
        with app.app_context():
            from app.services.ingestion import run
            n = run()
            log.info("[Scheduler] Fetched %s records", n)

    def predict_job():
        with app.app_context():
            import requests
            try:
                requests.post("http://localhost:8080/api/predict", timeout=30)
                log.info("[Scheduler] Predictions updated")
            except Exception as e:
                log.error("[Scheduler] Predict error: %s", e)

    def train_job():
        with app.app_context():
            import requests
            try:
                requests.post("http://localhost:8080/api/train", timeout=120)
                log.info("[Scheduler] Models retrained")
            except Exception as e:
                log.error("[Scheduler] Train error: %s", e)

    interval = app.config.get("FETCH_INTERVAL_MIN", 15)
    s.add_job(fetch_job,   IntervalTrigger(minutes=interval), id="fetch",   replace_existing=True)
    s.add_job(predict_job, IntervalTrigger(hours=1),          id="predict", replace_existing=True)
    s.add_job(train_job,   IntervalTrigger(hours=24),         id="train",   replace_existing=True)
    s.start()
    log.info("[Scheduler] Started. Fetch every %s min.", interval)
