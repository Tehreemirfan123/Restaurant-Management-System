import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv


ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_FILE)


# Business timezone (Pakistan is a fixed UTC+5, no DST). Used so "today"
# reflects the restaurant's local day, not the server's UTC day.
BUSINESS_TZ = timezone(timedelta(hours=int(os.getenv("BUSINESS_UTC_OFFSET", "5"))))


def local_today():
    """Current date in the business timezone."""
    return datetime.now(BUSINESS_TZ).date()


# Secret used to sign JWTs. MUST be overridden in production via the .env file.
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "change-me-in-production-this-is-not-secure",
)

JWT_ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080")  # 7 days
)

# Flat delivery fee (Rs.) added to delivery orders. Matches the brochure's
# "Delivery: Rs. 80 within 3 km".
DELIVERY_FEE = Decimal(os.getenv("DELIVERY_FEE", "80"))
