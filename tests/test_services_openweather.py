"""
Unit Tests — OpenWeatherMap Service
"""
from unittest.mock import patch, MagicMock
from app.services.openweather import fetch


class TestOpenWeatherService:

    def _mock_responses(self, mock_get):
        """Helper to set up mock API responses."""
        ap_resp = MagicMock()
        ap_resp.json.return_value = {
            "list": [{"main": {"aqi": 2}, "components": {
                "pm2_5": 12.5, "pm10": 20.3,
                "o3": 40.1, "no2": 15.2,
                "so2": 2.1,  "co": 350.0
            }}]
        }
        wx_resp = MagicMock()
        wx_resp.json.return_value = {
            "sys":  {"country": "IE"},
            "main": {"temp": 12.0, "humidity": 78},
            "wind": {"speed": 5.2, "deg": 180}
        }
        mock_get.side_effect = [ap_resp, wx_resp]

    @patch("app.services.openweather.requests.get")
    def test_fetch_returns_dict(self, mock_get):
        """OpenWeatherMap fetch should return a dict."""
        self._mock_responses(mock_get)
        result = fetch("test_key", "Dublin", 53.3498, -6.2603)
        assert result is not None
        assert isinstance(result, dict)

    @patch("app.services.openweather.requests.get")
    def test_fetch_source_is_openweathermap(self, mock_get):
        """Source should be OpenWeatherMap."""
        self._mock_responses(mock_get)
        result = fetch("test_key", "Dublin", 53.3498, -6.2603)
        assert result["source"] == "OpenWeatherMap"

    @patch("app.services.openweather.requests.get")
    def test_fetch_temperature_present(self, mock_get):
        """Temperature should be present."""
        self._mock_responses(mock_get)
        result = fetch("test_key", "Dublin", 53.3498, -6.2603)
        assert result["temperature"] == 12.0

    @patch("app.services.openweather.requests.get")
    def test_fetch_humidity_present(self, mock_get):
        """Humidity should be present."""
        self._mock_responses(mock_get)
        result = fetch("test_key", "Dublin", 53.3498, -6.2603)
        assert result["humidity"] == 78

    @patch("app.services.openweather.requests.get")
    def test_fetch_aqi_scaled(self, mock_get):
        """AQI should be scaled (index * 50)."""
        self._mock_responses(mock_get)
        result = fetch("test_key", "Dublin", 53.3498, -6.2603)
        assert result["aqi"] == 2 * 50

    @patch("app.services.openweather.requests.get")
    def test_fetch_returns_none_on_error(self, mock_get):
        """Should return None on network error."""
        mock_get.side_effect = Exception("API error")
        result = fetch("test_key", "Dublin", 53.3498, -6.2603)
        assert result is None

    @patch("app.services.openweather.requests.get")
    def test_fetch_pm25_present(self, mock_get):
        """PM2.5 should be present in result."""
        self._mock_responses(mock_get)
        result = fetch("test_key", "Dublin", 53.3498, -6.2603)
        assert result["pm25"] == 12.5

    @patch("app.services.openweather.requests.get")
    def test_fetch_city_matches(self, mock_get):
        """City name should match input."""
        self._mock_responses(mock_get)
        result = fetch("test_key", "Dublin", 53.3498, -6.2603)
        assert result["city"] == "Dublin"
