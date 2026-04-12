"""
Unit Tests — Predictions Endpoints
"""
import json
from unittest.mock import patch, MagicMock


class TestPredictionsEndpoint:

    @patch("app.routes.api.get_db")
    def test_predictions_returns_200(self, mock_get_db, client, sample_prediction):
        """Predictions endpoint should return 200."""
        mock_conn   = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [sample_prediction]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = client.get("/api/predictions")
        assert response.status_code == 200

    @patch("app.routes.api.get_db")
    def test_predictions_returns_list(self, mock_get_db, client, sample_prediction):
        """Predictions should return a list."""
        mock_conn   = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [sample_prediction]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = client.get("/api/predictions")
        data = json.loads(response.data)
        assert isinstance(data, list)

    @patch("app.routes.api.get_db")
    def test_predictions_contains_risk_level(self, mock_get_db, client, sample_prediction):
        """Predictions should contain risk_level field."""
        mock_conn   = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [sample_prediction]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = client.get("/api/predictions")
        data = json.loads(response.data)
        assert len(data) > 0
        assert "risk_level" in data[0]

    @patch("app.routes.api.get_db")
    def test_predictions_valid_risk_levels(self, mock_get_db, client, sample_prediction):
        """Risk levels should be one of the valid categories."""
        mock_conn   = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [sample_prediction]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        valid_levels = [
            "Good", "Moderate",
            "Unhealthy for Sensitive Groups",
            "Unhealthy", "Very Unhealthy", "Hazardous"
        ]
        response = client.get("/api/predictions")
        data = json.loads(response.data)
        for row in data:
            assert row["risk_level"] in valid_levels

    @patch("app.routes.api.get_db")
    def test_predictions_filter_by_city(self, mock_get_db, client, sample_prediction):
        """Predictions should accept city filter."""
        mock_conn   = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [sample_prediction]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = client.get("/api/predictions?city=Dublin")
        assert response.status_code == 200

    @patch("app.routes.api.get_db")
    @patch("app.routes.api.predict_city")
    def test_predict_post_returns_200(self, mock_predict, mock_get_db, client, sample_prediction):
        """POST /api/predict should return 200."""
        mock_conn   = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"city": "Dublin", "aqi": 45}
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn
        mock_predict.return_value = [sample_prediction]

        response = client.post("/api/predict")
        assert response.status_code == 200

    @patch("app.routes.api.get_db")
    def test_risk_score_range(self, mock_get_db, client, sample_prediction):
        """Risk score should be between 0 and 100."""
        mock_conn   = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [sample_prediction]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = client.get("/api/predictions")
        data = json.loads(response.data)
        for row in data:
            assert 0 <= row["risk_score"] <= 100
