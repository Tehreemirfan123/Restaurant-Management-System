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
