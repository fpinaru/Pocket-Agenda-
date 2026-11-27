from fastapi.testclient import TestClient
import backend
client = TestClient(backend.app)

def test_home_reports_backend_running():
    response = client.get("/")
    assert response.status_code ==200
    assert response.json() == {"message": "Backend is sleeping"}
