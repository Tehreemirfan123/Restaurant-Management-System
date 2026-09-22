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


# ---------------------------------------------------------------------------
# Payment gateway configuration
# ---------------------------------------------------------------------------
# All gateway settings come from the environment so secrets never live in the
# database or the repo. To go live, set PAYMENT_GATEWAY=jazzcash (or easypaisa)
# and fill in the merchant credentials below, then restart the app.
#
# The default is "sandbox": a built-in simulator that mimics a hosted-checkout
# redirect flow end to end (no credentials, no real money) so the whole
# order -> pay -> callback -> reconciliation path is testable locally.
PAYMENT_GATEWAY = os.getenv("PAYMENT_GATEWAY", "sandbox").lower()

# Public base URL of THIS backend (where the gateway sends the customer back
# and posts server-to-server callbacks) and of the customer site.
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# JazzCash merchant credentials (from the JazzCash merchant portal).
JAZZCASH_MERCHANT_ID = os.getenv("JAZZCASH_MERCHANT_ID", "")
JAZZCASH_PASSWORD = os.getenv("JAZZCASH_PASSWORD", "")
JAZZCASH_INTEGRITY_SALT = os.getenv("JAZZCASH_INTEGRITY_SALT", "")
JAZZCASH_POST_URL = os.getenv(
    "JAZZCASH_POST_URL",
    # JazzCash sandbox page-redirect endpoint; swap to the live URL in prod.
    "https://sandbox.jazzcash.com.pk/CustomerPortal/transactionmanagement/merchantform",
)

# Easypaisa merchant credentials (from the Easypaisa/Telenor merchant portal).
EASYPAISA_STORE_ID = os.getenv("EASYPAISA_STORE_ID", "")
EASYPAISA_HASH_KEY = os.getenv("EASYPAISA_HASH_KEY", "")
EASYPAISA_POST_URL = os.getenv(
    "EASYPAISA_POST_URL",
    "https://easypaisa.com.pk/easypay/Index.jsf",
)

# Shared secret used to sign the sandbox simulator's callbacks so the verify
# path is exercised exactly like a real gateway's signature check.
SANDBOX_SALT = os.getenv("SANDBOX_SALT", "sandbox-integrity-salt")
