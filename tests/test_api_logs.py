"""
Unit Tests — Logs and Metrics Endpoints
"""
import json
from unittest.mock import patch, MagicMock


class TestLogsEndpoint:

    @patch("app.routes.api.get_db")
    def test_logs_returns_200(self, mock_get_db, client):
        """Logs endpoint should return 200."""
        mock_conn   = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = client.get("/api/logs")
        assert response.status_code == 200

    @patch("app.routes.api.get_db")
    def test_logs_returns_list(self, mock_get_db, client):
        """Logs endpoint should return a list."""
        mock_conn   = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{
            "id": 1, "city": "Dublin", "source": "WAQI",
            "status": "ok", "message": "", "logged_at": "2026-04-10T10:00:00"
        }]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = client.get("/api/logs")
        data = json.loads(response.data)
        assert isinstance(data, list)

    @patch("app.routes.api.get_db")
    def test_logs_contains_status(self, mock_get_db, client):
        """Each log should have a status field."""
        mock_conn   = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{
            "id": 1, "city": "Dublin", "source": "WAQI",
            "status": "ok", "message": "", "logged_at": "2026-04-10T10:00:00"
        }]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = client.get("/api/logs")
        data = json.loads(response.data)
        assert len(data) > 0
        assert "status" in data[0]

    @patch("app.routes.api.get_db")
    def test_logs_valid_statuses(self, mock_get_db, client):
        """Log statuses should be valid values."""
        mock_conn   = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {"id": 1, "city": "Dublin", "source": "WAQI",
             "status": "ok", "message": "", "logged_at": "2026-04-10T10:00:00"},
            {"id": 2, "city": "London", "source": "OpenWeatherMap",
             "status": "error", "message": "timeout", "logged_at": "2026-04-10T10:00:00"},
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = client.get("/api/logs")
        data = json.loads(response.data)
        valid = ["ok", "error", "no_data"]
        for row in data:
            assert row["status"] in valid


class TestMetricsEndpoint:

    @patch("app.routes.api.get_db")
    def test_metrics_returns_200(self, mock_get_db, client):
        """Metrics endpoint should return 200."""
        mock_conn   = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = client.get("/api/metrics")
        assert response.status_code == 200

    @patch("app.routes.api.get_db")
    def test_metrics_accuracy_range(self, mock_get_db, client):
        """Model accuracy should be between 0 and 1."""
        mock_conn   = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{
            "id": 1, "model": "RandomForest",
            "accuracy": 0.92, "f1": 0.91,
            "precision_": 0.90, "recall": 0.89,
            "mae": 0.1, "rmse": 0.2,
            "rows_used": 500, "trained_at": "2026-04-10T10:00:00"
        }]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = client.get("/api/metrics")
        data = json.loads(response.data)
        for row in data:
            assert 0.0 <= row["accuracy"] <= 1.0
            assert 0.0 <= row["f1"]       <= 1.0
