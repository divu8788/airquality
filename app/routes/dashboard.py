"""
Dashboard Route
"""
from flask import Blueprint, render_template_string
import os

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
def index():
    template_path = os.path.join(os.path.dirname(__file__), "../../templates/dashboard.html")
    with open(template_path) as f:
        return render_template_string(f.read())
