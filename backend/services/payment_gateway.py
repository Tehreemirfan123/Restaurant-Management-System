"""Payment gateway integration.

This module isolates everything to do with an external payment gateway behind
three functions the rest of the app calls:

    initiate_checkout(db, order, method)  -> where to send the customer to pay
    process_callback(db, params)          -> handle the gateway's response
    simulate_sandbox(db, txn_ref, ok)     -> the built-in test gateway

A gateway integration is always the same shape, whichever provider you use:

    1. INITIATE  – create a pending payment with our own unique reference,
       then hand the customer off to the gateway's hosted page (a redirect or
       an auto-submitting form) carrying a signed set of parameters.
    2. PAY       – the customer authorises the payment ON the gateway, so we
       never touch their card/wallet PIN.
    3. CALLBACK  – the gateway sends the result back (a browser redirect and/or
       a server-to-server webhook). We VERIFY the signature, match it to our
       pending payment by our reference, and mark it paid or failed.

The default provider is "sandbox": a local simulator that runs this exact flow
(including signature signing/verification) without any credentials, so the
whole path is testable. Switch to jazzcash/easypaisa via env (see core.config).
"""

import hashlib
import hmac
import secrets
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status

from core import config
from models.models import Order, Payment, PaymentMethodEnum, PaymentStatusEnum
from services.payment_service import _annotate, _paid_total


# --- helpers ---------------------------------------------------------------

def _hmac_sha256(key: str, message: str) -> str:
    """The signing primitive every provider here uses (hex, uppercase)."""
    return hmac.new(
        key.encode("utf-8"), message.encode("utf-8"), hashlib.sha256
    ).hexdigest().upper()


def _secure_hash(fields: dict, salt: str) -> str:
    """Build a gateway secure hash the JazzCash way: sort the fields by key,
    join their values with '&' after the salt, then HMAC-SHA256 with the salt.
    """
    ordered = [
        str(fields[k])
        for k in sorted(fields)
        if fields[k] not in (None, "")
        and k not in ("pp_SecureHash", "pp_secure_hash")
    ]
    message = salt + "&" + "&".join(ordered)
    return _hmac_sha256(salt, message)


def _new_txn_ref(order: Order) -> str:
    """A unique, human-traceable reference tied to the order number."""
    return f"MK{order.order_number}-{secrets.token_hex(4).upper()}"


def _amount_due(db, order: Order) -> Decimal:
    """How much to collect now: the advance if one is required and not yet
    paid, otherwise the whole outstanding balance.
    """
    from services.order_service import compute_advance
    from services.settings_service import get_settings

    paid = _paid_total(order)
    balance = Decimal(order.total_amount or 0) - paid
    if balance <= 0:
        return Decimal("0")

    settings = get_settings(db)
    required, advance = compute_advance(order.total_amount, order.category, settings)
    if required and paid <= 0 and advance > 0:
        return advance
    return balance


def _provider_salt(provider: str) -> str:
    if provider == "jazzcash":
        return config.JAZZCASH_INTEGRITY_SALT
    if provider == "easypaisa":
        return config.EASYPAISA_HASH_KEY
    return config.SANDBOX_SALT


# --- 1. initiate -----------------------------------------------------------

def initiate_checkout(db, order: Order, method: str) -> dict:
    """Create a pending payment and return where/how to send the customer."""
    amount = _amount_due(db, order)
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This order is already fully paid",
        )

    try:
        method_enum = PaymentMethodEnum(method)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported payment method: {method}",
        )

    provider = config.PAYMENT_GATEWAY
    txn_ref = _new_txn_ref(order)

    payment = Payment(
        order_id=order.id,
        amount=amount,
        method=method_enum,
        status=PaymentStatusEnum.pending,
        gateway=provider,
        transaction_ref=txn_ref,
    )
    db.add(payment)
    db.commit()

    if provider == "jazzcash":
        return _initiate_jazzcash(order, amount, txn_ref)
    if provider == "easypaisa":
        return _initiate_easypaisa(order, amount, txn_ref)
    return _initiate_sandbox(amount, txn_ref)


def _initiate_sandbox(amount: Decimal, txn_ref: str) -> dict:
    # The "hosted page" is served by this same backend (see the router).
    return {
        "provider": "sandbox",
        "http_method": "GET",
        "checkout_url": f"{config.API_BASE_URL}/payments/sandbox/{txn_ref}",
        "fields": {},
        "transaction_ref": txn_ref,
        "amount": str(amount),
    }


def _initiate_jazzcash(order: Order, amount: Decimal, txn_ref: str) -> dict:
    now = datetime.now(timezone.utc)
    fields = {
        "pp_Version": "1.1",
        "pp_TxnType": "MWALLET",
        "pp_Language": "EN",
        "pp_MerchantID": config.JAZZCASH_MERCHANT_ID,
        "pp_Password": config.JAZZCASH_PASSWORD,
        "pp_TxnRefNo": txn_ref,
        # JazzCash amounts are in paisa (no decimal point).
        "pp_Amount": str(int(Decimal(amount) * 100)),
        "pp_TxnCurrency": "PKR",
        "pp_TxnDateTime": now.strftime("%Y%m%d%H%M%S"),
        "pp_BillReference": f"order{order.order_number}",
        "pp_Description": f"Mehak's Kitchen order #{order.order_number}",
        "pp_ReturnURL": f"{config.API_BASE_URL}/payments/callback",
    }
    fields["pp_SecureHash"] = _secure_hash(fields, config.JAZZCASH_INTEGRITY_SALT)
    return {
        "provider": "jazzcash",
        "http_method": "POST",
        "checkout_url": config.JAZZCASH_POST_URL,
        "fields": fields,
        "transaction_ref": txn_ref,
        "amount": str(amount),
    }


def _initiate_easypaisa(order: Order, amount: Decimal, txn_ref: str) -> dict:
    fields = {
        "storeId": config.EASYPAISA_STORE_ID,
        "orderRefNum": txn_ref,
        "amount": f"{Decimal(amount):.2f}",
        "postBackURL": f"{config.API_BASE_URL}/payments/callback",
        "paymentMethod": "MA_PAYMENT_METHOD",
    }
    fields["merchantHashedReq"] = _secure_hash(fields, config.EASYPAISA_HASH_KEY)
    return {
        "provider": "easypaisa",
        "http_method": "POST",
        "checkout_url": config.EASYPAISA_POST_URL,
        "fields": fields,
        "transaction_ref": txn_ref,
        "amount": str(amount),
    }


# --- 3. callback -----------------------------------------------------------

# Success response codes differ per provider.
_SUCCESS_CODES = {"jazzcash": "000", "easypaisa": "0000", "sandbox": "000"}


def process_callback(db, params: dict) -> tuple[Payment | None, bool, str]:
    """Verify a gateway callback and settle the matching payment.

    Returns (payment, ok, message). Idempotent: a repeated callback for an
    already-paid payment is accepted without double counting.
    """
    txn_ref = (
        params.get("pp_TxnRefNo")
        or params.get("orderRefNum")
        or params.get("transaction_ref")
    )
    if not txn_ref:
        return None, False, "Missing transaction reference"

    from sqlalchemy import select

    payment = db.scalar(
        select(Payment).where(Payment.transaction_ref == txn_ref)
    )
    if payment is None:
        return None, False, "Unknown transaction reference"

    provider = payment.gateway or config.PAYMENT_GATEWAY
    salt = _provider_salt(provider)

    # 1) Verify the signature so we can trust the payload.
    received_hash = (
        params.get("pp_SecureHash") or params.get("merchantHashedReq") or ""
    )
    expected_hash = _secure_hash(
        {k: v for k, v in params.items()
         if k not in ("pp_SecureHash", "merchantHashedReq")},
        salt,
    )
    if not hmac.compare_digest(received_hash.upper(), expected_hash):
        return payment, False, "Signature verification failed"

    # 2) Idempotency: ignore a repeat for an already-settled payment.
    if payment.status == PaymentStatusEnum.paid:
        return _annotate(payment), True, "Already paid"

    # 3) Apply the result.
    code = (
        params.get("pp_ResponseCode")
        or params.get("responseCode")
        or ""
    )
    message = (
        params.get("pp_ResponseMessage")
        or params.get("responseMessage")
        or ""
    )
    gateway_txn_id = (
        params.get("pp_RetreivalReferenceNo")
        or params.get("pp_AuthCode")
        or params.get("transactionId")
        or None
    )

    if code == _SUCCESS_CODES.get(provider, "000"):
        payment.status = PaymentStatusEnum.paid
        payment.paid_at = datetime.now(timezone.utc)
        payment.reference = gateway_txn_id or payment.transaction_ref
        payment.note = message or "Paid via gateway"
        db.commit()
        return _annotate(payment), True, "Payment successful"

    payment.status = PaymentStatusEnum.failed
    payment.note = message or f"Declined (code {code})"
    db.commit()
    return _annotate(payment), False, payment.note


# --- built-in sandbox gateway ---------------------------------------------

def simulate_sandbox(db, txn_ref: str, success: bool) -> tuple[Payment | None, bool, str]:
    """Stand in for the real gateway: build a signed callback and process it.

    This is what makes the sandbox realistic — the simulated gateway signs the
    response with the shared salt, and process_callback verifies it just like a
    live provider's callback.
    """
    from sqlalchemy import select

    payment = db.scalar(
        select(Payment).where(Payment.transaction_ref == txn_ref)
    )
    if payment is None:
        return None, False, "Unknown transaction reference"

    params = {
        "pp_TxnRefNo": txn_ref,
        "pp_Amount": str(int(Decimal(payment.amount) * 100)),
        "pp_ResponseCode": "000" if success else "999",
        "pp_ResponseMessage": (
            "Transaction Successful" if success else "Transaction Cancelled"
        ),
        "pp_RetreivalReferenceNo": f"SBX{secrets.token_hex(5).upper()}",
    }
    params["pp_SecureHash"] = _secure_hash(params, config.SANDBOX_SALT)
    return process_callback(db, params)
