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


def test_costing_reflects_recipe_and_costs(client, auth_headers):
    # Inventory item with a unit cost.
    inv = client.post(
        "/inventory",
        headers=auth_headers,
        json={"name": "Costing Rice", "unit": "kg", "quantity": 100, "unit_cost": 200},
    ).json()

    # Dish priced 300 with Rs.30 packaging.
    dish = client.post(
        "/menu",
        headers=auth_headers,
        json={
            "name": "Costing Dish",
            "description": None,
            "price": 300,
            "category": "mains",
            "packaging_cost": 30,
            "image_url": None,
            "available": True,
        },
    ).json()

    # Recipe uses 0.5 kg rice -> ingredient cost 100.
    client.post(
        "/recipes",
        headers=auth_headers,
        json={
            "menu_item_id": dish["id"],
            "ingredients": [
                {"inventory_item_id": inv["id"], "quantity": 0.5}
            ],
        },
    )

    rows = client.get("/reports/costing", headers=auth_headers).json()
    row = next(r for r in rows if r["menu_item_id"] == dish["id"])

    assert float(row["ingredient_cost"]) == 100
    assert float(row["packaging_cost"]) == 30
    assert float(row["variable_cost"]) == 130
    # 300 - 130 = 170
    assert float(row["contribution"]) == 170
    assert row["has_recipe"] is True
