import os
import sys
from pathlib import Path

# App modules use imports rooted at the backend/ directory (e.g.
# `from database.database import ...`), so backend/ must be on sys.path.
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from database.database import Base, get_db
from main import app

# Tests share a single client IP and run many requests per minute, so disable
# the rate limiter for the suite (it's exercised separately, not here).
from core.rate_limit import limiter

limiter.enabled = False

# Load TEST_DATABASE_URL (and friends) from backend/.env
load_dotenv(BACKEND_DIR / ".env")


TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    raise RuntimeError(
        "TEST_DATABASE_URL is not configured"
    )


engine = create_engine(
    TEST_DATABASE_URL,
)


TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture(
    scope="session",
    autouse=True,
)
def setup_database():
    Base.metadata.create_all(
        bind=engine
    )

    yield

    Base.metadata.drop_all(
        bind=engine
    )


@pytest.fixture
def db_session():
    # Each test runs inside an outer transaction that is rolled back at the end,
    # so nothing a test writes leaks into other tests. The session joins that
    # transaction using SAVEPOINTs, so the app's own db.commit() calls are
    # contained and undone on teardown (true test isolation).
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(
        bind=connection,
        join_transaction_mode="create_savepoint",
    )

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(
    db_session: Session,
):
    def override_get_db():
        yield db_session

    app.dependency_overrides[
        get_db
    ] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client, db_session):
    """Create an admin, log in, and return Authorization headers.

    Most back-office endpoints (customers, tables, inventory, recipes)
    require a logged-in staff member.
    """
    import uuid

    from core.security import hash_password
    from models.models import RoleEnum, Staff

    # Tests share one database without per-test rollback, so the username
    # must be unique across the whole run to avoid clashes.
    username = f"tester-admin-{uuid.uuid4().hex[:8]}"

    staff = Staff(
        username=username,
        full_name="Tester Admin",
        hashed_password=hash_password("testpass123"),
        role=RoleEnum.admin,
    )
    db_session.add(staff)
    db_session.commit()

    response = client.post(
        "/auth/login",
        data={
            "username": username,
            "password": "testpass123",
        },
    )

    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}