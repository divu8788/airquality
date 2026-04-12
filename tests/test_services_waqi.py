"""
Unit Tests — WAQI Service
"""
import pytest
from unittest.mock import patch, MagicMock
from app.services.waqi import fetch


class TestWAQIService:

    @patch("app.services.waqi.requests.get")
    def test_fetch_returns_dict_on_success(self, mock_get):
        """WAQI fetch should return a dict on success."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "status": "ok",
            "data": {
                "aqi": 45,
                "city": {"name": "Dublin", "geo": [53.3498, -6.2603]},
                "iaqi": {
                    "pm25": {"v": 12.5},
                    "pm10": {"v": 20.3},
                    "t":    {"v": 12.0},
                    "h":    {"v": 78.0},
                }
            }
        }
        mock_get.return_value = mock_resp

        result = fetch("test_token", "Dublin", "dublin")
        assert result is not None
        assert isinstance(result, dict)

    @patch("app.services.waqi.requests.get")
    def test_fetch_returns_none_on_bad_status(self, mock_get):
        """WAQI fetch should return None if status is not ok."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"status": "error", "data": "Unknown station"}
        mock_get.return_value = mock_resp

        result = fetch("test_token", "Dublin", "dublin")
        assert result is None

    @patch("app.services.waqi.requests.get")
    def test_fetch_returns_none_on_dash_aqi(self, mock_get):
        """WAQI fetch should handle aqi='-' gracefully."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "status": "ok",
            "data": {
                "aqi": "-",
                "city": {"name": "Dublin", "geo": [53.3498, -6.2603]},
                "iaqi": {}
            }
        }
        mock_get.return_value = mock_resp

        result = fetch("test_token", "Dublin", "dublin")
        assert result is not None
        assert result["aqi"] is None

    @patch("app.services.waqi.requests.get")
    def test_fetch_returns_none_on_exception(self, mock_get):
        """WAQI fetch should return None on network error."""
        mock_get.side_effect = Exception("Connection timeout")
        result = fetch("test_token", "Dublin", "dublin")
        assert result is None

    @patch("app.services.waqi.requests.get")
    def test_fetch_contains_required_keys(self, mock_get):
        """WAQI result should contain all required keys."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "status": "ok",
            "data": {
                "aqi": 45,
                "city": {"name": "Dublin", "geo": [53.3498, -6.2603]},
                "iaqi": {"pm25": {"v": 12.5}}
            }
        }
        mock_get.return_value = mock_resp

        result = fetch("test_token", "Dublin", "dublin")
        required = ["city", "source", "aqi", "pm25", "pm10",
                    "temperature", "humidity", "fetched_at"]
        for key in required:
            assert key in result

    @patch("app.services.waqi.requests.get")
    def test_fetch_source_is_waqi(self, mock_get):
        """Source field should always be WAQI."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "status": "ok",
            "data": {
                "aqi": 45,
                "city": {"name": "Dublin", "geo": [53.3498, -6.2603]},
                "iaqi": {}
            }
        }
        mock_get.return_value = mock_resp

        result = fetch("test_token", "Dublin", "dublin")
        assert result["source"] == "WAQI"

    @patch("app.services.waqi.requests.get")
    def test_fetch_city_name_matches(self, mock_get):
        """City name in result should match input."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "status": "ok",
            "data": {
                "aqi": 45,
                "city": {"name": "Dublin", "geo": [53.3498, -6.2603]},
                "iaqi": {}
            }
        }
        mock_get.return_value = mock_resp

        result = fetch("test_token", "Dublin", "dublin")
        assert result["city"] == "Dublin"
