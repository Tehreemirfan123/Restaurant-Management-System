def _make_menu_item(client, auth_headers, name):
    return client.post(
        "/menu",
        headers=auth_headers,
        json={
            "name": name,
            "description": None,
            "price": 200,
            "category": "mains",
            "image_url": None,
            "available": True,
        },
    ).json()


def _place(client, item):
    return client.post(
        "/orders",
        json={
            "order_type": "pickup",
            "items": [{"menu_item_id": item["id"], "quantity": 1}],
        },
    )


def test_status_is_public(client):
    resp = client.get("/settings/status")
    assert resp.status_code == 200
    assert "accepting_orders" in resp.json()


def test_settings_update_requires_admin(client):
    resp = client.put("/settings", json={"accepting_orders": False})
    assert resp.status_code == 401


def test_not_accepting_blocks_orders(client, auth_headers):
    item = _make_menu_item(client, auth_headers, "Gate Dish A")

    client.put(
        "/settings",
        headers=auth_headers,
        json={"accepting_orders": False},
    )
    blocked = _place(client, item)
    assert blocked.status_code == 400

    # Re-open for other tests.
    client.put(
        "/settings",
        headers=auth_headers,
        json={"accepting_orders": True, "daily_order_cap": None},
    )
    assert _place(client, item).status_code == 201


def test_settings_expanded_fields(client, auth_headers):
    resp = client.get("/settings", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    for key in ("restaurant_name", "delivery_fee", "delivery_radius_km"):
        assert key in data


def test_configurable_delivery_fee_applies_to_orders(client, auth_headers):
    # Set a custom delivery fee.
    client.put(
        "/settings",
        headers=auth_headers,
        json={"delivery_fee": 150, "accepting_orders": True},
    )

    item = _make_menu_item(client, auth_headers, "Fee Dish")
    resp = client.post(
        "/orders",
        json={
            "order_type": "delivery",
            "delivery_address": "somewhere",
            "items": [{"menu_item_id": item["id"], "quantity": 1}],
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert float(data["delivery_fee"]) == 150
    assert float(data["total_amount"]) == 350  # 200 + 150

    # Reset so other tests see the default fee.
    client.put("/settings", headers=auth_headers, json={"delivery_fee": 80})
