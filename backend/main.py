import logging
import os

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text

from core.rate_limit import limiter
from database.database import engine
from routers.auth import router as auth_router
from routers.config import router as config_router
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


# ---------------------------------------------------------------------------
# Logging — structured, level configurable via LOG_LEVEL.
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("mehak_kitchen")


# The database schema is managed by Alembic migrations, not create_all.
# Run `alembic upgrade head` before starting the app on a fresh database.
app = FastAPI(
    title="Restaurant Management System API",
    version="1.0.0",
)

# Rate limiting (see core.rate_limit and the @limiter.limit decorators on the
# public endpoints in the routers).
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


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


# ---------------------------------------------------------------------------
# Global exception handler — log the real error server-side, return a clean,
# generic message to the client so internals/tracebacks are never leaked.
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


app.include_router(auth_router)
app.include_router(config_router)
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
    return {"message": "Restaurant Management System API is running"}


@app.get("/health")
def health_check():
    """Readiness/liveness probe. Returns 503 (not 200) when the database is
    unreachable so Kubernetes will restart / stop routing to a broken pod.
    The underlying error is logged, never returned to the caller.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception:
        logger.exception("Health check failed: database unreachable")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "database": "disconnected"},
        )
