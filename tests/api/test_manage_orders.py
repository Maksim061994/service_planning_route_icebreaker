from fastapi.testclient import TestClient
from app.main_app import app  # replace with the actual name of your FastAPI app


client = TestClient(app)


def test_orders_with_authorization():
    # Send a login request
    login_response = client.post("/users/login", json={"login": "present", "password": "@Z&WSSv?5|AVhTeD"})  # replace with your actual login endpoint and credentials
    assert login_response.status_code == 200

    # Retrieve the authorization token from the login response
    token = login_response.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}

    # Send a request to get the list of orders with the authorization token
    response = client.get("/orders", headers=headers)  # replace with the actual endpoint
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    # Send a request to create an order with the authorization token
    response = client.post("/orders/add", headers=headers, json={
        "name_ship": "Test",
        "class_ship": "Test Class",
        "point_start": "Архангельск",
        "point_end": "Лаптевых - 4 (юг)",
        "speed": 10,
        "date_start_swim": "2023-01-01"
    })  # replace with the actual endpoint and request body
    assert response.status_code == 200
    assert "order_id" in response.json()

    # Send a request to delete an order with the authorization token
    order_id = response.json()["order_id"]
    response = client.post("/orders/delete", headers=headers, json={
        "order_id": order_id,
    })
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}