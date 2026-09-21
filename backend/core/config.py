import os
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv


ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_FILE)


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
