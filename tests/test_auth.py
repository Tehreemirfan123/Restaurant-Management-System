from core.security import hash_password
from models.models import RoleEnum, Staff


def _make_staff(
    db_session,
    username="admin",
    password="admin123",
    role=RoleEnum.admin,
):
    staff = Staff(
        username=username,
        full_name="Test User",
        hashed_password=hash_password(password),
        role=role,
    )
    db_session.add(staff)
    db_session.commit()
    return staff


def _login(client, username, password):
    return client.post(
        "/auth/login",
        data={
            "username": username,
            "password": password,
        },
    )


def test_login_success(client, db_session):
    _make_staff(db_session, "loginuser", "secret123")

    response = _login(client, "loginuser", "secret123")

    assert response.status_code == 200

    data = response.json()

    assert data["token_type"] == "bearer"
    assert data["role"] == "admin"
    assert "access_token" in data


def test_login_wrong_password(client, db_session):
    _make_staff(db_session, "wrongpw", "secret123")

    response = _login(client, "wrongpw", "badpass")

    assert response.status_code == 401


def test_login_unknown_user(client):
    response = _login(client, "ghost", "whatever")

    assert response.status_code == 401


def test_me_requires_token(client):
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_me_returns_current_staff(client, db_session):
    _make_staff(db_session, "meuser", "secret123", RoleEnum.staff)

    token = _login(client, "meuser", "secret123").json()[
        "access_token"
    ]

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["username"] == "meuser"
    assert response.json()["role"] == "staff"


def test_staff_creation_requires_admin(client, db_session):
    _make_staff(db_session, "plainstaff", "secret123", RoleEnum.staff)

    token = _login(client, "plainstaff", "secret123").json()[
        "access_token"
    ]

    response = client.post(
        "/auth/staff",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "newperson",
            "full_name": "New Person",
            "password": "secret123",
            "role": "staff",
        },
    )

    assert response.status_code == 403


def test_admin_can_create_staff(client, db_session):
    _make_staff(db_session, "bossadmin", "secret123", RoleEnum.admin)

    token = _login(client, "bossadmin", "secret123").json()[
        "access_token"
    ]

    response = client.post(
        "/auth/staff",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "createdstaff",
            "full_name": "Created Staff",
            "password": "secret123",
            "role": "staff",
        },
    )

    assert response.status_code == 201
    assert response.json()["username"] == "createdstaff"
