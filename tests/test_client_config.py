def test_client_config_is_public_and_non_secret(client):
    resp = client.get("/client-config")
    assert resp.status_code == 200
    data = resp.json()

    # Identity + brand + terminology come through from client.config.yaml.
    assert data["client"]["vertical"] == "restaurant"
    assert data["brand"]["name"] == "Mehak's Kitchen"
    assert data["terminology"]["customer"] == "Customer"
    assert "menu" in data["modules"]["enabled"]
    assert data["payment_methods"] == [
        "cash",
        "bank_transfer",
        "jazzcash",
        "easypaisa",
    ]

    # Server-side rule params and role matrix must NOT be exposed publicly.
    assert "roles" not in data
    assert "payments" not in data
    assert "delivery" not in data
