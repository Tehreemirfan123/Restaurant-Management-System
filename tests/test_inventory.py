def test_inventory_requires_auth(client):
    response = client.get("/inventory")
    assert response.status_code == 401


def test_create_inventory_item(client, auth_headers):
    response = client.post(
        "/inventory",
        headers=auth_headers,
        json={
            "name": "Rice",
            "unit": "kg",
            "quantity": 50,
            "reorder_level": 10,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Rice"
    assert data["unit"] == "kg"
    assert data["quantity"] == "50.000"


def test_duplicate_inventory_name_rejected(client, auth_headers):
    client.post(
        "/inventory",
        headers=auth_headers,
        json={"name": "Flour", "unit": "kg", "quantity": 20},
    )

    response = client.post(
        "/inventory",
        headers=auth_headers,
        json={"name": "Flour", "unit": "kg", "quantity": 5},
    )

    assert response.status_code == 400


def test_update_inventory_quantity(client, auth_headers):
    created = client.post(
        "/inventory",
        headers=auth_headers,
        json={"name": "Sugar", "unit": "kg", "quantity": 30},
    ).json()

    response = client.put(
        f"/inventory/{created['id']}",
        headers=auth_headers,
        json={"quantity": 25},
    )

    assert response.status_code == 200
    assert response.json()["quantity"] == "25.000"
