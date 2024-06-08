from fastapi.testclient import TestClient
from app.main import app  # replace with the actual name of your FastAPI app


client = TestClient(app)


def test_nsi_with_authorization():
    # Send a login request
    login_response = client.post("/users/login", json={"login": "present", "password": "@Z&WSSv?5|AVhTeD"})  # replace with your actual login endpoint and credentials
    assert login_response.status_code == 200

    # Retrieve the authorization token from the login response
    token = login_response.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}

    # Send a request to get the list of edges with the authorization token
    response = client.get("/nsi/edges", headers=headers)  # replace with the actual endpoint
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    # Send a request to get the list of points with the authorization token
    response = client.get("/nsi/points", headers=headers)  # replace with the actual endpoint
    assert response.status_code == 200
    assert isinstance(response.json(), list)