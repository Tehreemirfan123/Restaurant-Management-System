def test_customers_require_auth(client):
    response = client.get("/customers")
    assert response.status_code == 401


def test_create_and_get_customer(client, auth_headers):
    response = client.post(
        "/customers",
        headers=auth_headers,
        json={
            "name": "Ali Khan",
            "phone": "03001234567",
            "email": "ali@example.com",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Ali Khan"
    assert data["phone"] == "03001234567"

    customer_id = data["id"]

    get_response = client.get(
        f"/customers/{customer_id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 200
    assert get_response.json()["id"] == customer_id


def test_update_customer(client, auth_headers):
    created = client.post(
        "/customers",
        headers=auth_headers,
        json={"name": "Old Name"},
    ).json()

    response = client.put(
        f"/customers/{created['id']}",
        headers=auth_headers,
        json={"name": "New Name"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


def test_delete_customer(client, auth_headers):
    created = client.post(
        "/customers",
        headers=auth_headers,
        json={"name": "Delete Me"},
    ).json()

    response = client.delete(
        f"/customers/{created['id']}",
        headers=auth_headers,
    )
    assert response.status_code == 204

    missing = client.get(
        f"/customers/{created['id']}",
        headers=auth_headers,
    )
    assert missing.status_code == 404


# Ordering with a phone find-or-creates a customer and tracks repeats
def test_order_captures_and_tracks_repeat_customer(client, auth_headers):
    menu_item = client.post(
        "/menu",
        headers=auth_headers,
        json={
            "name": "Repeat Dish",
            "description": None,
            "price": 200,
            "category": "mains",
            "image_url": None,
            "available": True,
        },
    ).json()

    phone = "03009998877"

    def place():
        return client.post(
            "/orders",
            json={
                "order_type": "pickup",
                "customer_name": "Repeat Customer",
                "customer_phone": phone,
                "items": [
                    {"menu_item_id": menu_item["id"], "quantity": 1}
                ],
            },
        )

    assert place().status_code == 201
    assert place().status_code == 201

    # The customer should now exist once with two orders.
    customers = client.get("/customers", headers=auth_headers).json()
    match = [c for c in customers if c["phone"] == phone]
    assert len(match) == 1
    assert match[0]["order_count"] == 2

    # Reports should count them as a repeat customer.
    summary = client.get(
        "/reports/summary", headers=auth_headers
    ).json()
    assert summary["repeat_customers"] >= 1
    assert summary["total_customers"] >= 1
