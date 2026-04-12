"""
Unit Tests — ML Predictor
"""
import pytest
import pandas as pd
import numpy as np
from app.ml.predictor import aqi_to_risk, RISK_MAP, SCORE_MAP


class TestAQIToRisk:

    def test_good_range(self):
        """AQI 0-50 should be Good."""
        assert aqi_to_risk(0)  == "Good"
        assert aqi_to_risk(25) == "Good"
        assert aqi_to_risk(50) == "Good"

    def test_moderate_range(self):
        """AQI 51-100 should be Moderate."""
        assert aqi_to_risk(51)  == "Moderate"
        assert aqi_to_risk(75)  == "Moderate"
        assert aqi_to_risk(100) == "Moderate"

    def test_sensitive_range(self):
        """AQI 101-150 should be Unhealthy for Sensitive Groups."""
        assert aqi_to_risk(101) == "Unhealthy for Sensitive Groups"
        assert aqi_to_risk(150) == "Unhealthy for Sensitive Groups"

    def test_unhealthy_range(self):
        """AQI 151-200 should be Unhealthy."""
        assert aqi_to_risk(151) == "Unhealthy"
        assert aqi_to_risk(200) == "Unhealthy"

    def test_very_unhealthy_range(self):
        """AQI 201-300 should be Very Unhealthy."""
        assert aqi_to_risk(201) == "Very Unhealthy"
        assert aqi_to_risk(300) == "Very Unhealthy"

    def test_hazardous_range(self):
        """AQI 301+ should be Hazardous."""
        assert aqi_to_risk(301) == "Hazardous"
        assert aqi_to_risk(500) == "Hazardous"

    def test_none_returns_unknown(self):
        """None AQI should return Unknown."""
        assert aqi_to_risk(None) == "Unknown"

    def test_float_aqi(self):
        """Float AQI should work correctly."""
        assert aqi_to_risk(45.5) == "Good"
        assert aqi_to_risk(75.9) == "Moderate"


class TestRiskScoreMap:

    def test_all_risk_levels_have_scores(self):
        """All risk levels should have a score."""
        levels = ["Good", "Moderate", "Unhealthy for Sensitive Groups",
                  "Unhealthy", "Very Unhealthy", "Hazardous"]
        for level in levels:
            assert level in SCORE_MAP

    def test_scores_are_ordered(self):
        """Risk scores should increase with severity."""
        assert SCORE_MAP["Good"]        < SCORE_MAP["Moderate"]
        assert SCORE_MAP["Moderate"]    < SCORE_MAP["Unhealthy"]
        assert SCORE_MAP["Unhealthy"]   < SCORE_MAP["Very Unhealthy"]
        assert SCORE_MAP["Very Unhealthy"] < SCORE_MAP["Hazardous"]

    def test_scores_in_valid_range(self):
        """All scores should be between 0 and 100."""
        for level, score in SCORE_MAP.items():
            assert 0 <= score <= 100


class TestMLTraining:

    def test_train_requires_minimum_rows(self, app):
        """Training should fail gracefully with insufficient data."""
        with app.app_context():
            from app.ml.predictor import train
            df = pd.DataFrame([{
                "aqi": 45, "pm25": 12, "pm10": 20,
                "o3": 40, "no2": 15, "so2": 2, "co": 0.5,
                "temperature": 12, "humidity": 78, "wind_speed": 5
            }])
            result = train(df)
            assert result == {}

    def test_train_returns_metrics_dict(self, app):
        """Training should return metrics for each model."""
        with app.app_context():
            from app.ml.predictor import train
            rows = []
            for i in range(60):
                aqi = (i % 6) * 60
                rows.append({
                    "aqi": aqi, "pm25": aqi/5, "pm10": aqi/3,
                    "o3": 40, "no2": 15, "so2": 2, "co": 0.5,
                    "temperature": 12, "humidity": 78, "wind_speed": 5
                })
            df = pd.DataFrame(rows)
            result = train(df)
            assert isinstance(result, dict)
            if result:
                for model_name, metrics in result.items():
                    assert "accuracy"  in metrics
                    assert "f1"        in metrics
                    assert "precision_" in metrics
                    assert "recall"    in metrics
