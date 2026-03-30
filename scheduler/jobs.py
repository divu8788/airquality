"""
APScheduler Jobs
- Every N minutes: fetch data from all 3 APIs
- Every hour: run ML predictions
- Every day: retrain models
"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)
_scheduler = None


def _fetch_job(app):
    with app.app_context():
        from app.services.ingestion_service import fetch_and_store_all
        n = fetch_and_store_all()
        logger.info(f"[Scheduler] fetch_and_store_all → {n} records")


def _predict_job(app):
    with app.app_context():
        from app.services.prediction_service import run_predictions_all_cities
        run_predictions_all_cities()
        logger.info("[Scheduler] Predictions updated.")


def _train_job(app):
    with app.app_context():
        from app.services.training_service import retrain_models
        retrain_models()
        logger.info("[Scheduler] Models retrained.")


def start_scheduler(app):
    global _scheduler
    interval = app.config.get("FETCH_INTERVAL_MINUTES", 15)
    _scheduler = BackgroundScheduler(daemon=True)

    _scheduler.add_job(
        func=_fetch_job, args=[app],
        trigger=IntervalTrigger(minutes=interval),
        id="fetch_data", replace_existing=True,
    )
    _scheduler.add_job(
        func=_predict_job, args=[app],
        trigger=IntervalTrigger(hours=1),
        id="run_predictions", replace_existing=True,
    )
    _scheduler.add_job(
        func=_train_job, args=[app],
        trigger=IntervalTrigger(hours=24),
        id="retrain_models", replace_existing=True,
    )

    _scheduler.start()
    logger.info(f"[Scheduler] Started — fetch every {interval} min, predict hourly, retrain daily.")
