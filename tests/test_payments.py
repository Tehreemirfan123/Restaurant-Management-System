def create_test_order(client, auth_headers):
    menu_response = client.post(
        "/menu",
        headers=auth_headers,
        json={
            "name": "Chicken Biryani",
            "description": "Chicken biryani",
            "price": 450,
            "category": "mains",
            "image_url": None,
            "available": True,
        },
    )

    assert menu_response.status_code == 201

    menu_item = menu_response.json()

    order_response = client.post(
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

    assert order_response.status_code == 201

    return order_response.json()


def test_create_payment(client, auth_headers):
    order = create_test_order(client, auth_headers)

    response = client.post(
        "/payments",
        headers=auth_headers,
        json={
            "order_id": order["id"],
            "method": "cash",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["order_id"] == order["id"]
    assert data["amount"] == "900.00"
    assert data["method"] == "cash"
    assert data["status"] == "paid"
    assert data["paid_at"] is not None


def test_payment_uses_order_total(client, auth_headers):
    order = create_test_order(client, auth_headers)

    response = client.post(
        "/payments",
        headers=auth_headers,
        json={
            "order_id": order["id"],
            "method": "card",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["amount"] == order["total_amount"]


def test_payment_order_not_found(client, auth_headers):
    response = client.post(
        "/payments",
        headers=auth_headers,
        json={
            "order_id": "00000000-0000-0000-0000-000000000000",
            "method": "cash",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


def test_full_payment_blocks_further_payment(client, auth_headers):
    order = create_test_order(client, auth_headers)

    first_response = client.post(
        "/payments",
        headers=auth_headers,
        json={
            "order_id": order["id"],
            "method": "cash",
        },
    )

    assert first_response.status_code == 201

    # The order is fully paid, so a second full payment is rejected.
    second_response = client.post(
        "/payments",
        headers=auth_headers,
        json={
            "order_id": order["id"],
            "method": "card",
        },
    )

    assert second_response.status_code == 400
    assert "already fully paid" in second_response.json()["detail"]


def test_advance_then_balance(client, auth_headers):
    order = create_test_order(client, auth_headers)  # total 900

    advance = client.post(
        "/payments",
        headers=auth_headers,
        json={"order_id": order["id"], "method": "jazzcash", "amount": 450},
    )
    assert advance.status_code == 201
    assert advance.json()["status"] == "paid"

    # Order now shows a partial payment with a remaining balance.
    fetched = client.get(f"/orders/{order['id']}").json()
    assert fetched["payment_status"] == "partial"
    assert float(fetched["amount_paid"]) == 450
    assert float(fetched["balance_due"]) == 450

    # Paying the balance settles the order.
    balance = client.post(
        "/payments",
        headers=auth_headers,
        json={"order_id": order["id"], "method": "cash", "amount": 450},
    )
    assert balance.status_code == 201

    settled = client.get(f"/orders/{order['id']}").json()
    assert settled["payment_status"] == "paid"
    assert float(settled["balance_due"]) == 0


def test_payment_cannot_exceed_balance(client, auth_headers):
    order = create_test_order(client, auth_headers)  # total 900
    resp = client.post(
        "/payments",
        headers=auth_headers,
        json={"order_id": order["id"], "method": "cash", "amount": 1000},
    )
    assert resp.status_code == 400
    assert "exceeds" in resp.json()["detail"]


def test_reconciliation_lists_payments_and_outstanding(client, auth_headers):
    from datetime import date

    order = create_test_order(client, auth_headers)  # total 900
    client.post(
        "/payments",
        headers=auth_headers,
        json={
            "order_id": order["id"],
            "method": "easypaisa",
            "amount": 400,
            "reference": "EP-123",
        },
    )

    today = date.today().isoformat()
    resp = client.get(f"/payments/reconciliation?date={today}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["payment_count"] >= 1
    assert float(data["total_collected"]) >= 400
    methods = {m["method"] for m in data["by_method"]}
    assert "easypaisa" in methods
    # The partially-paid order shows up as outstanding with the right balance.
    ours = [o for o in data["outstanding"] if o["order_number"] == order["order_number"]]
    assert ours and float(ours[0]["balance_due"]) == 500


def test_custom_order_requires_advance(client, auth_headers):
    menu_item = client.post(
        "/menu",
        headers=auth_headers,
        json={
            "name": "Custom Platter",
            "price": 900,
            "category": "mains",
            "available": True,
        },
    ).json()

    order = client.post(
        "/orders",
        json={
            "category": "custom",
            "items": [{"menu_item_id": menu_item["id"], "quantity": 1}],
        },
    ).json()

    assert order["category"] == "custom"
    assert order["advance_required"] is True
    # 50% of 900 by default.
    assert float(order["advance_amount"]) == 450


def test_get_payment(client, auth_headers):
    order = create_test_order(client, auth_headers)

    create_response = client.post(
        "/payments",
        headers=auth_headers,
        json={
            "order_id": order["id"],
            "method": "cash",
        },
    )

    payment = create_response.json()

    response = client.get(
        f"/payments/{payment['id']}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == payment["id"]
    assert data["order_id"] == order["id"]
    assert data["amount"] == "900.00"
    assert data["method"] == "cash"
    assert data["status"] == "paid"


def test_get_payment_not_found(client, auth_headers):
    response = client.get(
        "/payments/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Payment not found"

def test_payment_requires_auth(client):
    response = client.post(
        "/payments",
        json={
            "order_id": "00000000-0000-0000-0000-000000000000",
            "method": "cash",
        },
    )
    assert response.status_code == 401
