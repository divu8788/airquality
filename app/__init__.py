"""
Flask Application Factory
"""
from flask import Flask
from flask_cors import CORS
from config.settings import Config
from app.models.database import init_db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app)

    # Initialize database tables
    with app.app_context():
        init_db()

    # Register blueprints
    from app.routes.api import api_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.predictions import predictions_bp

    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(dashboard_bp, url_prefix="/")
    app.register_blueprint(predictions_bp, url_prefix="/api/predictions")

    return app
