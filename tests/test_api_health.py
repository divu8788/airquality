"""
Unit Tests — Health Endpoint
"""
import json


class TestHealthEndpoint:

    def test_health_returns_200(self, client):
        """Health endpoint should return 200 OK."""
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_returns_json(self, client):
        """Health endpoint should return JSON."""
        response = client.get("/api/health")
        assert response.content_type == "application/json"

    def test_health_returns_ok_status(self, client):
        """Health endpoint should return status ok."""
        response = client.get("/api/health")
        data = json.loads(response.data)
        assert data["status"] == "ok"

    def test_health_method_not_allowed(self, client):
        """Health endpoint should not accept POST."""
        response = client.post("/api/health")
        assert response.status_code == 405

    def test_invalid_route_returns_404(self, client):
        """Invalid route should return 404."""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
