def test_tables_require_auth(client):
    response = client.get("/tables")
    assert response.status_code == 401


def test_create_table(client, auth_headers):
    response = client.post(
        "/tables",
        headers=auth_headers,
        json={"number": 1, "capacity": 4},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["number"] == 1
    assert data["capacity"] == 4
    assert data["status"] == "available"


def test_duplicate_table_number_rejected(client, auth_headers):
    client.post(
        "/tables",
        headers=auth_headers,
        json={"number": 5, "capacity": 2},
    )

    response = client.post(
        "/tables",
        headers=auth_headers,
        json={"number": 5, "capacity": 6},
    )

    assert response.status_code == 400


def test_update_table_status(client, auth_headers):
    created = client.post(
        "/tables",
        headers=auth_headers,
        json={"number": 9, "capacity": 4},
    ).json()

    response = client.put(
        f"/tables/{created['id']}",
        headers=auth_headers,
        json={"status": "occupied"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "occupied"
