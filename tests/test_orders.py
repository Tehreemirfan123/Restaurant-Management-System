# Create Order
def test_create_order(client, auth_headers):
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

    menu_item = menu_response.json()

    response = client.post(
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

    assert response.status_code == 201

    data = response.json()

    assert data["total_amount"] == "900.00"
    assert data["status"] == "received"
    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 2
    assert data["items"][0]["unit_price"] == "450.00"

# Nonexistent Menu Item
def test_create_order_with_invalid_menu_item(client):
    response = client.post(
        "/orders",
        json={
            "items": [
                {
                    "menu_item_id": "00000000-0000-0000-0000-000000000000",
                    "quantity": 1,
                }
            ]
        },
    )

    assert response.status_code == 404

# Unavailable Menu Item
def test_create_order_with_unavailable_item(client, auth_headers):
    menu_response = client.post(
        "/menu",
        headers=auth_headers,
        json={
            "name": "Unavailable Burger",
            "description": None,
            "price": 500,
            "category": "mains",
            "image_url": None,
            "available": False,
        },
    )

    menu_item = menu_response.json()

    response = client.post(
        "/orders",
        json={
            "items": [
                {
                    "menu_item_id": menu_item["id"],
                    "quantity": 1,
                }
            ]
        },
    )

    assert response.status_code == 400

# Dine-in order linked to a table
def test_create_dine_in_order_with_table(client, auth_headers):
    menu_item = client.post(
        "/menu",
        headers=auth_headers,
        json={
            "name": "Seekh Kebab",
            "description": None,
            "price": 300,
            "category": "starters",
            "image_url": None,
            "available": True,
        },
    ).json()

    table = client.post(
        "/tables",
        headers=auth_headers,
        json={"number": 21, "capacity": 4},
    ).json()

    response = client.post(
        "/orders",
        json={
            "order_type": "dine_in",
            "table_id": table["id"],
            "items": [
                {"menu_item_id": menu_item["id"], "quantity": 3}
            ],
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["order_type"] == "dine_in"
    assert data["table_id"] == table["id"]
    assert data["total_amount"] == "900.00"


# Dine-in without a table should be rejected
def test_dine_in_requires_table(client, auth_headers):
    menu_item = client.post(
        "/menu",
        headers=auth_headers,
        json={
            "name": "Naan",
            "description": None,
            "price": 40,
            "category": "mains",
            "image_url": None,
            "available": True,
        },
    ).json()

    response = client.post(
        "/orders",
        json={
            "order_type": "dine_in",
            "items": [
                {"menu_item_id": menu_item["id"], "quantity": 1}
            ],
        },
    )

    assert response.status_code == 400


# Delivery order adds the delivery fee and needs an address
def test_delivery_order_adds_fee(client, auth_headers):
    menu_item = client.post(
        "/menu",
        headers=auth_headers,
        json={
            "name": "Delivery Dish",
            "description": None,
            "price": 200,
            "category": "mains",
            "image_url": None,
            "available": True,
        },
    ).json()

    response = client.post(
        "/orders",
        json={
            "order_type": "delivery",
            "delivery_address": "123 Al Hamad Road, Lahore",
            "items": [{"menu_item_id": menu_item["id"], "quantity": 1}],
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["order_type"] == "delivery"
    assert data["delivery_fee"] == "80.00"
    # 200 item + 80 delivery
    assert data["total_amount"] == "280.00"
    assert data["delivery_address"] == "123 Al Hamad Road, Lahore"


def test_delivery_requires_address(client, auth_headers):
    menu_item = client.post(
        "/menu",
        headers=auth_headers,
        json={
            "name": "Delivery Dish No Address",
            "description": None,
            "price": 200,
            "category": "mains",
            "image_url": None,
            "available": True,
        },
    ).json()

    response = client.post(
        "/orders",
        json={
            "order_type": "delivery",
            "items": [{"menu_item_id": menu_item["id"], "quantity": 1}],
        },
    )

    assert response.status_code == 400


def test_pickup_order_has_no_fee(client, auth_headers):
    menu_item = client.post(
        "/menu",
        headers=auth_headers,
        json={
            "name": "Pickup Dish",
            "description": None,
            "price": 200,
            "category": "mains",
            "image_url": None,
            "available": True,
        },
    ).json()

    response = client.post(
        "/orders",
        json={
            "order_type": "pickup",
            "items": [{"menu_item_id": menu_item["id"], "quantity": 1}],
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["order_type"] == "pickup"
    assert data["delivery_fee"] == "0.00"
    assert data["total_amount"] == "200.00"


# Distance-based delivery: beyond the base radius adds per-km charge
def test_delivery_fee_scales_with_distance(client, auth_headers):
    menu_item = client.post(
        "/menu",
        headers=auth_headers,
        json={
            "name": "Distance Dish",
            "description": None,
            "price": 200,
            "category": "mains",
            "image_url": None,
            "available": True,
        },
    ).json()

    # 5 km with base radius 3 km, base fee 80, per-km 26 -> 80 + 2*26 = 132
    response = client.post(
        "/orders",
        json={
            "order_type": "delivery",
            "delivery_address": "5 km away",
            "delivery_distance_km": 5,
            "items": [{"menu_item_id": menu_item["id"], "quantity": 1}],
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert float(data["delivery_fee"]) == 132
    assert float(data["total_amount"]) == 332  # 200 + 132
    assert float(data["delivery_distance_km"]) == 5


def test_delivery_within_radius_is_base_fee(client, auth_headers):
    menu_item = client.post(
        "/menu",
        headers=auth_headers,
        json={
            "name": "Near Dish",
            "description": None,
            "price": 200,
            "category": "mains",
            "image_url": None,
            "available": True,
        },
    ).json()

    response = client.post(
        "/orders",
        json={
            "order_type": "delivery",
            "delivery_address": "2 km away",
            "delivery_distance_km": 2,
            "items": [{"menu_item_id": menu_item["id"], "quantity": 1}],
        },
    )
    assert response.status_code == 201
    assert float(response.json()["delivery_fee"]) == 80
