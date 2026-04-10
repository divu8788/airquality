"""
Unit Tests — Fetch Endpoint
"""
import json
from unittest.mock import patch


class TestFetchEndpoint:

    @patch("app.routes.api.ingest")
    def test_fetch_returns_200(self, mock_ingest, client):
        """Fetch endpoint should return 200."""
        mock_ingest.return_value = 10
        response = client.post("/api/fetch")
        assert response.status_code == 200

    @patch("app.routes.api.ingest")
    def test_fetch_returns_inserted_count(self, mock_ingest, client):
        """Fetch should return number of inserted records."""
        mock_ingest.return_value = 10
        response = client.post("/api/fetch")
        data = json.loads(response.data)
        assert data["status"]   == "ok"
        assert data["inserted"] == 10

    @patch("app.routes.api.ingest")
    def test_fetch_zero_inserted(self, mock_ingest, client):
        """Fetch should handle zero inserts gracefully."""
        mock_ingest.return_value = 0
        response = client.post("/api/fetch")
        data = json.loads(response.data)
        assert data["status"]   == "ok"
        assert data["inserted"] == 0

    @patch("app.routes.api.ingest")
    def test_fetch_handles_error(self, mock_ingest, client):
        """Fetch should return 500 on error."""
        mock_ingest.side_effect = Exception("API connection failed")
        response = client.post("/api/fetch")
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data["status"] == "error"

    def test_fetch_get_not_allowed(self, client):
        """Fetch endpoint should not accept GET."""
        response = client.get("/api/fetch")
        assert response.status_code == 405

    @patch("app.routes.api.ingest")
    def test_fetch_inserts_from_two_sources(self, mock_ingest, client):
        """Fetch should insert from WAQI and OpenWeatherMap (2 sources x 5 cities = 10)."""
        mock_ingest.return_value = 10
        response = client.post("/api/fetch")
        data = json.loads(response.data)
        assert data["inserted"] == 10
