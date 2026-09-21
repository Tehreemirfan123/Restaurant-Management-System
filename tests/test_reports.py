def test_reports_require_admin(client):
    response = client.get("/reports/summary")
    assert response.status_code == 401


def test_reports_summary_shape(client, auth_headers):
    response = client.get("/reports/summary", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    for key in (
        "total_revenue",
        "today_revenue",
        "total_orders",
        "today_orders",
        "top_items",
        "low_stock",
    ):
        assert key in data

    assert isinstance(data["top_items"], list)
    assert isinstance(data["low_stock"], list)


def test_reports_reflect_activity(client, auth_headers):
    # Create a menu item, order it, and pay — then it should show in totals.
    menu_item = client.post(
        "/menu",
        headers=auth_headers,
        json={
            "name": "Report Test Dish",
            "description": None,
            "price": 200,
            "category": "mains",
            "image_url": None,
            "available": True,
        },
    ).json()

    order = client.post(
        "/orders",
        json={
            "items": [{"menu_item_id": menu_item["id"], "quantity": 2}]
        },
    ).json()

    client.post(
        "/payments",
        json={"order_id": order["id"], "method": "cash"},
    )

    data = client.get("/reports/summary", headers=auth_headers).json()

    assert float(data["total_revenue"]) >= 400
    assert data["total_orders"] >= 1
    names = [t["name"] for t in data["top_items"]]
    assert "Report Test Dish" in names
