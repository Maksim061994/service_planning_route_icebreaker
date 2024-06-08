from fastapi.testclient import TestClient
from app.main import app  # replace with the actual name of your FastAPI app


client = TestClient(app)


def test_icebreakers_with_authorization():
    # Send a login request
    login_response = client.post("/users/login", json={"login": "present", "password": "@Z&WSSv?5|AVhTeD"})  # replace with your actual login endpoint and credentials
    assert login_response.status_code == 200

    # Retrieve the authorization token from the login response
    token = login_response.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}

    # Send a request to get the list of icebreakers with the authorization token
    response = client.get("/icebreakers", headers=headers)  # replace with the actual endpoint
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    # Send a request to create an icebreaker with the authorization token
    response = client.post("/icebreakers/add", headers=headers, json={
        "name_icebreaker": "Test",
        "class_icebreaker": "Test Class",
        "speed": 10,
        "start_position": "Test Position"
    })  # replace with the actual endpoint and request body
    assert response.status_code == 200
    assert "icebreaker_id" in response.json()

    # Send a request to delete an icebreaker with the authorization token
    icebreaker_id = response.json()["icebreaker_id"]
    response = client.post("/icebreakers/delete", headers=headers, json={
        "icebreaker_id": icebreaker_id,
    })
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

