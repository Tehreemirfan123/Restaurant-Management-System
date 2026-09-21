def test_waste_requires_auth(client):
    assert client.get("/waste").status_code == 401


def test_log_waste_computes_cost(client, auth_headers):
    item = client.post(
        "/inventory",
        headers=auth_headers,
        json={
            "name": "Waste Rice",
            "unit": "kg",
            "quantity": 50,
            "unit_cost": 200,
        },
    ).json()

    response = client.post(
        "/waste",
        headers=auth_headers,
        json={
            "inventory_item_id": item["id"],
            "quantity": 2,
            "description": "spoiled",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["item_name"] == "Waste Rice"
    # 2 kg x Rs.200 = 400
    assert float(data["cost"]) == 400


def test_general_waste_without_item(client, auth_headers):
    response = client.post(
        "/waste",
        headers=auth_headers,
        json={"quantity": 1, "description": "general kitchen waste"},
    )

    assert response.status_code == 201
    assert response.json()["item_name"] is None
