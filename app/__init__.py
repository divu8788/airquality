from flask import Flask
from flask_cors import CORS
from config.settings import Config
from app.models.database import init_db


def create_app():
    app = Flask(__name__, template_folder="../templates")
    app.config.from_object(Config)
    CORS(app)

    with app.app_context():
        init_db()

    from app.routes.main import main_bp
    from app.routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    return app
