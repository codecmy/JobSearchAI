from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_registration_and_profile():
    response = client.post("/api/v1/auth/register", json={
        "email": "test-careeros@example.com",
        "password": "secure123",
        "full_name": "Test Candidate",
    })
    assert response.status_code in (200, 409)
    if response.status_code == 409:
        response = client.post("/api/v1/auth/login", json={
            "email": "test-careeros@example.com", "password": "secure123"})
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    profile = client.get("/api/v1/candidates/me", headers=headers)
    assert profile.status_code == 200
    assert "headline" in profile.json()
