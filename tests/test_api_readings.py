"""
Unit Tests — Readings Endpoints
"""
import json
import pytest
from unittest.mock import patch, MagicMock


class TestReadingsEndpoint:

    @patch("app.routes.api.get_db")
    def test_readings_returns_200(self, mock_get_db, client, sample_reading):
        """Readings endpoint should return 200."""
        mock_conn   = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [sample_reading]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = client.get("/api/readings")
        assert response.status_code == 200

    @patch("app.routes.api.get_db")
    def test_readings_returns_list(self, mock_get_db, client, sample_reading):
        """Readings endpoint should return a list."""
        mock_conn   = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [sample_reading]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = client.get("/api/readings")
        data = json.loads(response.data)
        assert isinstance(data, list)

    @patch("app.routes.api.get_db")
    def test_readings_empty_db(self, mock_get_db, client):
        """Readings endpoint should return empty list if no data."""
        mock_conn   = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = client.get("/api/readings")
        data = json.loads(response.data)
        assert data == []

    @patch("app.routes.api.get_db")
    def test_readings_filter_by_city(self, mock_get_db, client, sample_reading):
        """Readings endpoint should accept city filter."""
        mock_conn   = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [sample_reading]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = client.get("/api/readings?city=Dublin")
        assert response.status_code == 200

    @patch("app.routes.api.get_db")
    def test_readings_limit_parameter(self, mock_get_db, client, sample_reading):
        """Readings endpoint should accept limit parameter."""
        mock_conn   = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [sample_reading]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = client.get("/api/readings?limit=10")
        assert response.status_code == 200

    @patch("app.routes.api.get_db")
    def test_readings_contains_expected_fields(self, mock_get_db, client, sample_reading):
        """Readings should contain all expected fields."""
        mock_conn   = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [sample_reading]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = client.get("/api/readings")
        data = json.loads(response.data)
        assert len(data) > 0
        row = data[0]
        for field in ["city", "source", "aqi", "pm25", "pm10"]:
            assert field in row

    @patch("app.routes.api.get_db")
    def test_readings_latest_returns_200(self, mock_get_db, client, sample_reading):
        """Latest readings endpoint should return 200."""
        mock_conn   = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [sample_reading]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = client.get("/api/readings/latest")
        assert response.status_code == 200

    @patch("app.routes.api.get_db")
    def test_readings_aqi_is_numeric(self, mock_get_db, client, sample_reading):
        """AQI values should be numeric."""
        mock_conn   = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [sample_reading]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = client.get("/api/readings")
        data = json.loads(response.data)
        for row in data:
            if row.get("aqi") is not None:
                assert isinstance(row["aqi"], (int, float))
