import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from database.database import engine
from routers.auth import router as auth_router
from routers.customers import router as customers_router
from routers.inventory import router as inventory_router
from routers.menu import router as menu_router
from routers.orders import router as orders_router
from routers.payment_gateway import router as payment_gateway_router
from routers.payments import router as payment_router
from routers.recipes import router as recipes_router
from routers.reports import router as reports_router
from routers.settings import router as settings_router
from routers.tables import router as tables_router
from routers.waste import router as waste_router


# The database schema is managed by Alembic migrations, not create_all.
# Run `alembic upgrade head` before starting the app on a fresh database.
app = FastAPI(
    title="Restaurant Management System API",
    version="1.0.0",
)


# Allowed origins are configurable via CORS_ORIGINS (comma-separated).
_cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost",
)
allow_origins = [o.strip() for o in _cors_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(menu_router)
app.include_router(orders_router)
# Public gateway endpoints first, then the staff-only payments router.
app.include_router(payment_gateway_router)
app.include_router(payment_router)
app.include_router(customers_router)
app.include_router(tables_router)
app.include_router(inventory_router)
app.include_router(recipes_router)
app.include_router(reports_router)
app.include_router(waste_router)
app.include_router(settings_router)


@app.get("/")
def root():
    return {
        "message": "Restaurant Management System API is running"
    }


@app.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected",
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
        }


@app.get("/api/test")
def test():
    return {
        "message": "Hello from Backend!"
    }