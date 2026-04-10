"""
Test Configuration and Fixtures
"""
import pytest
from unittest.mock import MagicMock, patch
from app import create_app


@pytest.fixture
def app():
    """Create test Flask application."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "DEBUG":   False,
    })
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def mock_db():
    """Mock database connection."""
    with patch("app.models.database.get_pool") as mock_pool:
        mock_conn   = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_pool.return_value.get_connection.return_value = mock_conn
        yield mock_conn, mock_cursor


@pytest.fixture
def sample_reading():
    """Sample reading data."""
    return {
        "id":            1,
        "city":          "Dublin",
        "country":       "Ireland",
        "latitude":      53.3498,
        "longitude":     -6.2603,
        "source":        "WAQI",
        "aqi":           45.0,
        "pm25":          12.5,
        "pm10":          20.3,
        "o3":            40.1,
        "no2":           15.2,
        "so2":           2.1,
        "co":            0.5,
        "temperature":   12.0,
        "humidity":      78.0,
        "wind_speed":    5.2,
        "wind_direction": 180.0,
        "fetched_at":    "2026-04-10T10:00:00",
    }


@pytest.fixture
def sample_prediction():
    """Sample prediction data."""
    return {
        "id":          1,
        "city":        "Dublin",
        "model":       "RandomForest",
        "risk_level":  "Good",
        "risk_score":  10,
        "confidence":  0.95,
        "predicted_at": "2026-04-10T10:00:00",
    }
