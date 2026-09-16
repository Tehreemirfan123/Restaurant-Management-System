def _make_menu_item(client, name="Karahi"):
    return client.post(
        "/menu",
        json={
            "name": name,
            "description": None,
            "price": 800,
            "category": "mains",
            "image_url": None,
            "available": True,
        },
    ).json()


def _make_inventory_item(client, auth_headers, name):
    return client.post(
        "/inventory",
        headers=auth_headers,
        json={"name": name, "unit": "kg", "quantity": 100},
    ).json()


def test_create_recipe_with_ingredients(client, auth_headers):
    menu_item = _make_menu_item(client, "Karahi")
    chicken = _make_inventory_item(client, auth_headers, "Chicken")
    tomato = _make_inventory_item(client, auth_headers, "Tomato")

    response = client.post(
        "/recipes",
        headers=auth_headers,
        json={
            "menu_item_id": menu_item["id"],
            "notes": "Signature karahi",
            "ingredients": [
                {"inventory_item_id": chicken["id"], "quantity": 0.5},
                {"inventory_item_id": tomato["id"], "quantity": 0.25},
            ],
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["menu_item_id"] == menu_item["id"]
    assert len(data["ingredients"]) == 2


def test_recipe_rejects_duplicate_menu_item(client, auth_headers):
    menu_item = _make_menu_item(client, "Nihari")

    first = client.post(
        "/recipes",
        headers=auth_headers,
        json={"menu_item_id": menu_item["id"], "ingredients": []},
    )
    assert first.status_code == 201

    second = client.post(
        "/recipes",
        headers=auth_headers,
        json={"menu_item_id": menu_item["id"], "ingredients": []},
    )
    assert second.status_code == 400


def test_recipe_rejects_unknown_inventory_item(client, auth_headers):
    menu_item = _make_menu_item(client, "Haleem")

    response = client.post(
        "/recipes",
        headers=auth_headers,
        json={
            "menu_item_id": menu_item["id"],
            "ingredients": [
                {
                    "inventory_item_id": "00000000-0000-0000-0000-000000000000",
                    "quantity": 1,
                }
            ],
        },
    )

    assert response.status_code == 404
