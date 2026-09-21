# CRUD tests
def test_create_menu_item(client, auth_headers):
    response = client.post(
        "/menu",
        headers=auth_headers,
        json={
            "name": "Chicken Biryani",
            "description": "Traditional Spicy Chicken Biryani with raita and Salad",
            "price": 350,
            "category": "mains",
            "image_url": None,
            "available": True,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Chicken Biryani"
    assert data["price"] == "350.00"
    assert data["category"] == "mains"
    assert data["available"] is True
    assert "id" in data


# Creating a menu item needs an admin
def test_create_menu_item_requires_admin(client):
    response = client.post(
        "/menu",
        json={
            "name": "No Auth Item",
            "description": None,
            "price": 100,
            "category": "mains",
            "image_url": None,
            "available": True,
        },
    )

    assert response.status_code == 401


# Getting Menu Item (public)
def test_get_menu_items(client, auth_headers):
    client.post(
        "/menu",
        headers=auth_headers,
        json={
            "name": "Burger",
            "description": "Beef burger",
            "price": 500,
            "category": "mains",
            "image_url": None,
            "available": True,
        },
    )

    response = client.get("/menu")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1

# Test validation
def test_create_menu_item_rejects_negative_price(client, auth_headers):
    response = client.post(
        "/menu",
        headers=auth_headers,
        json={
            "name": "Invalid Item",
            "description": None,
            "price": -100,
            "category": "mains",
            "image_url": None,
            "available": True,
        },
    )

    assert response.status_code == 422

# Invalid Category
def test_create_menu_item_rejects_invalid_category(client, auth_headers):
    response = client.post(
        "/menu",
        headers=auth_headers,
        json={
            "name": "Invalid Item",
            "description": None,
            "price": 100,
            "category": "pizza",
            "image_url": None,
            "available": True,
        },
    )

    assert response.status_code == 422


# Today's menu returns the day's dish plus day-agnostic specials
def test_todays_menu_filters_by_day(client, auth_headers):
    import datetime

    today = datetime.datetime.now(datetime.timezone.utc).strftime("%A").lower()
    other = "monday" if today != "monday" else "tuesday"

    # A dish for today, a dish for another day, and a day-agnostic special.
    client.post("/menu", headers=auth_headers, json={
        "name": "Todays Special Dish", "description": None, "price": 250,
        "category": "mains", "day_of_week": today,
        "image_url": None, "available": True,
    })
    client.post("/menu", headers=auth_headers, json={
        "name": "Other Day Dish", "description": None, "price": 250,
        "category": "mains", "day_of_week": other,
        "image_url": None, "available": True,
    })
    client.post("/menu", headers=auth_headers, json={
        "name": "Anyday Special", "description": None, "price": 700,
        "category": "mains", "day_of_week": None,
        "image_url": None, "available": True,
    })

    response = client.get("/menu/today")
    assert response.status_code == 200

    names = [i["name"] for i in response.json()]
    assert "Todays Special Dish" in names
    assert "Anyday Special" in names
    assert "Other Day Dish" not in names
