from fastapi.testclient import TestClient

from fast_api_server.main import app

client = TestClient(app)


def test_app_basic():
    response = client.get("/badroute")
    assert response.status_code == 404

    response = client.get("/v1alpha/libraries/hooli/functions")
    assert response.status_code == 200
