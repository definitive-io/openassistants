from fast_api_server.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_app_basic():
    response = client.get("/badroute")
    assert response.status_code == 404
