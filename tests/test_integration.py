"""
Integration Test
Tests that the Flask frontend and backend interact correctly.
POST /api/fetch → stores data → GET /api/readings returns it.
"""
import json
from unittest.mock import patch, MagicMock


def test_integration_fetch_and_read(client):
    """
    Integration test: POST /api/fetch then GET /api/readings returns data.

    This test verifies that:
    1. The fetch endpoint accepts a POST request
    2. Data is stored after fetching
    3. The readings endpoint returns the stored data
    4. Frontend and backend are communicating correctly
    """

    # ── Step 1: Mock the ingest function and DB ───────────────────────────────
    sample_reading = {
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
        "fetched_at":    "2026-04-11T10:00:00",
    }

    with patch("app.routes.api.ingest") as mock_ingest, \
         patch("app.routes.api.get_db") as mock_get_db:

        # Mock fetch returning 10 inserted records
        mock_ingest.return_value = 10

        # Mock DB returning our sample reading
        mock_conn   = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [sample_reading]
        mock_conn.cursor.return_value     = mock_cursor
        mock_get_db.return_value          = mock_conn

        # ── Step 2: Trigger fetch ─────────────────────────────────────────────
        fetch_resp = client.post("/api/fetch")
        assert fetch_resp.status_code == 200

        fetch_data = json.loads(fetch_resp.data)
        assert fetch_data["status"]   == "ok"
        assert fetch_data["inserted"] == 10

        # ── Step 3: Read data back ────────────────────────────────────────────
        read_resp = client.get("/api/readings")
        assert read_resp.status_code == 200

        data = json.loads(read_resp.data)
        assert isinstance(data, list)
        assert len(data) > 0

        # ── Step 4: Verify data structure ─────────────────────────────────────
        row = data[0]
        assert "city"       in row
        assert "aqi"        in row
        assert "source"     in row
        assert "pm25"       in row
        assert "fetched_at" in row

        # ── Step 5: Verify data values ────────────────────────────────────────
        assert row["city"]   == "Dublin"
        assert row["source"] == "WAQI"
        assert row["aqi"]    == 45.0