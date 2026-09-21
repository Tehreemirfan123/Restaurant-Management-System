def _make_order(client, auth_headers):
    menu_item = client.post(
        "/menu",
        headers=auth_headers,
        json={
            "name": "Feedback Dish",
            "description": None,
            "price": 200,
            "category": "mains",
            "image_url": None,
            "available": True,
        },
    ).json()
    return client.post(
        "/orders",
        json={
            "order_type": "pickup",
            "items": [{"menu_item_id": menu_item["id"], "quantity": 1}],
        },
    ).json()


def test_submit_and_read_feedback(client, auth_headers):
    order = _make_order(client, auth_headers)

    resp = client.post(
        f"/orders/{order['id']}/feedback",
        json={"rating": 5, "would_reorder": True, "comment": "Great!"},
    )
    assert resp.status_code == 201
    assert resp.json()["rating"] == 5

    got = client.get(f"/orders/{order['id']}/feedback")
    assert got.status_code == 200
    assert got.json()["comment"] == "Great!"


def test_feedback_only_once(client, auth_headers):
    order = _make_order(client, auth_headers)
    client.post(
        f"/orders/{order['id']}/feedback",
        json={"rating": 4},
    )
    second = client.post(
        f"/orders/{order['id']}/feedback",
        json={"rating": 3},
    )
    assert second.status_code == 400


def test_feedback_rating_range(client, auth_headers):
    order = _make_order(client, auth_headers)
    resp = client.post(
        f"/orders/{order['id']}/feedback",
        json={"rating": 9},
    )
    assert resp.status_code == 422
