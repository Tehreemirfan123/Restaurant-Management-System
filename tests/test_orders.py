# Create Order
def test_create_order(client):
    menu_response = client.post(
        "/menu",
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
def test_create_order_with_unavailable_item(client):
    menu_response = client.post(
        "/menu",
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