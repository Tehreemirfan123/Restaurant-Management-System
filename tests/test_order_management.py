def _order(client, auth_headers, qty=1):
    item = client.post(
        "/menu",
        headers=auth_headers,
        json={
            "name": "Mgmt Dish",
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
            "items": [{"menu_item_id": item["id"], "quantity": qty}],
        },
    ).json()


def test_cancel_requires_auth(client, auth_headers):
    order = _order(client, auth_headers)
    assert client.post(f"/orders/{order['id']}/cancel").status_code == 401


def test_cancel_refunds_paid_order(client, auth_headers):
    order = _order(client, auth_headers)
    client.post("/payments", json={"order_id": order["id"], "method": "cash"})

    resp = client.post(
        f"/orders/{order['id']}/cancel", headers=auth_headers
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"
    assert resp.json()["payment_status"] == "refunded"


def test_advance_payment_records_partial_amount(client, auth_headers):
    order = _order(client, auth_headers, qty=2)  # total 400
    resp = client.post(
        "/payments",
        json={"order_id": order["id"], "method": "jazzcash", "amount": 200},
    )
    assert resp.status_code == 201
    assert float(resp.json()["amount"]) == 200
    assert resp.json()["method"] == "jazzcash"


def test_status_change_requires_auth(client, auth_headers):
    order = _order(client, auth_headers)
    resp = client.patch(
        f"/orders/{order['id']}/status", json={"status": "preparing"}
    )
    assert resp.status_code == 401
