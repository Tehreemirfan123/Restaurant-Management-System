def create_test_order(client, auth_headers):
    menu_response = client.post(
        "/menu",
        headers=auth_headers,
        json={
            "name": "Chicken Biryani",
            "description": "Chicken biryani",
            "price": 450,
            "category": "mains",
            "image_url": None,
            "available": True,
        },
    )

    assert menu_response.status_code == 201

    menu_item = menu_response.json()

    order_response = client.post(
        "/orders",
        json={
            "items": [
                {
                    "menu_item_id": menu_item["id"],
                    "quantity": 2,
                }
            ]
        },
    )

    assert order_response.status_code == 201

    return order_response.json()


def test_create_payment(client, auth_headers):
    order = create_test_order(client, auth_headers)

    response = client.post(
        "/payments",
        json={
            "order_id": order["id"],
            "method": "cash",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["order_id"] == order["id"]
    assert data["amount"] == "900.00"
    assert data["method"] == "cash"
    assert data["status"] == "paid"
    assert data["paid_at"] is not None


def test_payment_uses_order_total(client, auth_headers):
    order = create_test_order(client, auth_headers)

    response = client.post(
        "/payments",
        json={
            "order_id": order["id"],
            "method": "card",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["amount"] == order["total_amount"]


def test_payment_order_not_found(client):
    response = client.post(
        "/payments",
        json={
            "order_id": "00000000-0000-0000-0000-000000000000",
            "method": "cash",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


def test_payment_already_exists(client, auth_headers):
    order = create_test_order(client, auth_headers)

    first_response = client.post(
        "/payments",
        json={
            "order_id": order["id"],
            "method": "cash",
        },
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/payments",
        json={
            "order_id": order["id"],
            "method": "card",
        },
    )

    assert second_response.status_code == 400
    assert (
        second_response.json()["detail"]
        == "Order has already been paid"
    )


def test_get_payment(client, auth_headers):
    order = create_test_order(client, auth_headers)

    create_response = client.post(
        "/payments",
        json={
            "order_id": order["id"],
            "method": "cash",
        },
    )

    payment = create_response.json()

    response = client.get(
        f"/payments/{payment['id']}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == payment["id"]
    assert data["order_id"] == order["id"]
    assert data["amount"] == "900.00"
    assert data["method"] == "cash"
    assert data["status"] == "paid"


def test_get_payment_not_found(client):
    response = client.get(
        "/payments/00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Payment not found"