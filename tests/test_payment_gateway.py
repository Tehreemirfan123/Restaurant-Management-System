def _menu_item(client, auth_headers, price=200):
    return client.post(
        "/menu",
        headers=auth_headers,
        json={"name": "Gateway Dish", "price": price, "category": "mains",
              "available": True},
    ).json()


def _order(client, item_id, qty=1, category="regular"):
    return client.post(
        "/orders",
        json={
            "category": category,
            "items": [{"menu_item_id": item_id, "quantity": qty}],
        },
    ).json()


def test_checkout_initiates_sandbox(client, auth_headers):
    item = _menu_item(client, auth_headers)
    order = _order(client, item["id"])  # total 200

    resp = client.post(
        "/payments/checkout",
        json={"order_id": order["id"], "method": "jazzcash"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["provider"] == "sandbox"
    assert float(data["amount"]) == 200
    assert "/payments/sandbox/" in data["checkout_url"]
    assert data["transaction_ref"].startswith("MK")


def test_sandbox_success_marks_order_paid(client, auth_headers):
    item = _menu_item(client, auth_headers)
    order = _order(client, item["id"])  # total 200

    checkout = client.post(
        "/payments/checkout",
        json={"order_id": order["id"], "method": "easypaisa"},
    ).json()
    ref = checkout["transaction_ref"]

    # The sandbox "hosted page" approve button posts here.
    done = client.post(
        f"/payments/sandbox/{ref}/complete",
        data={"result": "success"},
        follow_redirects=False,
    )
    assert done.status_code == 303
    assert f"/order/{order['id']}" in done.headers["location"]
    assert "paid=1" in done.headers["location"]

    status = client.get(f"/payments/checkout/{ref}/status").json()
    assert status["status"] == "paid"

    fetched = client.get(f"/orders/{order['id']}").json()
    assert fetched["payment_status"] == "paid"
    assert float(fetched["amount_paid"]) == 200


def test_sandbox_advance_collects_half(client, auth_headers):
    item = _menu_item(client, auth_headers, price=200)
    order = _order(client, item["id"], qty=2, category="custom")  # total 400

    checkout = client.post(
        "/payments/checkout",
        json={"order_id": order["id"], "method": "jazzcash"},
    ).json()
    assert float(checkout["amount"]) == 200  # 50% advance

    ref = checkout["transaction_ref"]
    client.post(
        f"/payments/sandbox/{ref}/complete",
        data={"result": "success"},
        follow_redirects=False,
    )

    fetched = client.get(f"/orders/{order['id']}").json()
    assert fetched["payment_status"] == "partial"
    assert float(fetched["amount_paid"]) == 200
    assert float(fetched["balance_due"]) == 200


def test_sandbox_failure_leaves_order_unpaid(client, auth_headers):
    item = _menu_item(client, auth_headers)
    order = _order(client, item["id"])

    checkout = client.post(
        "/payments/checkout",
        json={"order_id": order["id"], "method": "jazzcash"},
    ).json()
    ref = checkout["transaction_ref"]

    done = client.post(
        f"/payments/sandbox/{ref}/complete",
        data={"result": "fail"},
        follow_redirects=False,
    )
    assert done.status_code == 303
    assert "paid=0" in done.headers["location"]

    fetched = client.get(f"/orders/{order['id']}").json()
    assert fetched["payment_status"] in ("unpaid", None)
    assert float(fetched["amount_paid"]) == 0


def test_checkout_unknown_order(client):
    resp = client.post(
        "/payments/checkout",
        json={
            "order_id": "00000000-0000-0000-0000-000000000000",
            "method": "jazzcash",
        },
    )
    assert resp.status_code == 404
