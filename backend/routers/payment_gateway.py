"""Public payment-gateway endpoints (no auth — the customer pays here).

These are deliberately in their own router (separate from the staff-only
/payments router) because the customer and the gateway are not logged in:

    POST /payments/checkout                     start a payment, get where to go
    GET/POST /payments/callback                 the gateway returns the result
    GET  /payments/checkout/{ref}/status        poll a payment's status
    GET  /payments/sandbox/{ref}                the built-in test "hosted page"
    POST /payments/sandbox/{ref}/complete       approve/decline in the sandbox
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from core import config
from database.database import get_db
from models.models import Order, Payment
from schemas.schemas import CheckoutRequest, CheckoutResponse, CheckoutStatus
from services.payment_gateway import (
    initiate_checkout,
    process_callback,
    simulate_sandbox,
)


router = APIRouter(prefix="/payments", tags=["Payment gateway"])


@router.post("/checkout", response_model=CheckoutResponse)
def start_checkout(data: CheckoutRequest, db: Session = Depends(get_db)):
    order = db.get(Order, data.order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    return initiate_checkout(db, order, data.method.value)


def _finish(db: Session, params: dict) -> RedirectResponse:
    """Verify a callback and bounce the customer to their order page."""
    payment, ok, _ = process_callback(db, params)
    if payment is not None:
        order = db.get(Order, payment.order_id)
        target = f"{config.FRONTEND_URL}/order/{order.id}?paid={'1' if ok else '0'}"
    else:
        target = f"{config.FRONTEND_URL}/?paid=0"
    return RedirectResponse(url=target, status_code=status.HTTP_303_SEE_OTHER)


@router.post("/callback")
async def callback_post(request: Request, db: Session = Depends(get_db)):
    # Gateways post the result form-url-encoded; fall back to query params.
    form = await request.form()
    params = dict(form) or dict(request.query_params)
    return _finish(db, params)


@router.get("/callback")
def callback_get(request: Request, db: Session = Depends(get_db)):
    return _finish(db, dict(request.query_params))


@router.get(
    "/checkout/{txn_ref}/status", response_model=CheckoutStatus
)
def checkout_status(txn_ref: str, db: Session = Depends(get_db)):
    payment = db.scalar(
        select(Payment).where(Payment.transaction_ref == txn_ref)
    )
    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Unknown reference"
        )
    return {
        "transaction_ref": txn_ref,
        "status": payment.status,
        "order_id": payment.order_id,
        "amount": payment.amount,
    }


# --- built-in sandbox "hosted page" ---------------------------------------

@router.get("/sandbox/{txn_ref}", response_class=HTMLResponse)
def sandbox_page(txn_ref: str, db: Session = Depends(get_db)):
    payment = db.scalar(
        select(Payment).where(Payment.transaction_ref == txn_ref)
    )
    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Unknown reference"
        )
    order = db.get(Order, payment.order_id)
    amount = f"Rs. {float(payment.amount):.0f}"
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sandbox Payment — Mehak's Kitchen</title>
<style>
  body{{font-family:system-ui,Segoe UI,Arial,sans-serif;background:#791f2a;
       margin:0;display:flex;min-height:100vh;align-items:center;justify-content:center}}
  .card{{background:#fff;border-radius:16px;padding:28px;max-width:360px;width:90%;
        box-shadow:0 10px 40px rgba(0,0,0,.3);text-align:center}}
  h1{{font-size:18px;margin:0 0 4px;color:#5f1721}}
  .amt{{font-size:30px;font-weight:800;color:#5f1721;margin:14px 0}}
  p{{color:#555;font-size:13px;margin:4px 0}}
  .badge{{display:inline-block;background:#f6e8cb;color:#4a1119;border-radius:999px;
          padding:4px 10px;font-size:12px;margin-top:6px}}
  button{{width:100%;border:0;border-radius:10px;padding:12px;font-size:15px;
          font-weight:700;margin-top:10px;cursor:pointer}}
  .pay{{background:#16a34a;color:#fff}} .fail{{background:#eee;color:#333}}
  form{{margin:0}}
</style></head>
<body><div class="card">
  <h1>Sandbox Payment Gateway</h1>
  <p>Mehak's Kitchen · Order #{order.order_number}</p>
  <div class="amt">{amount}</div>
  <span class="badge">TEST MODE — no real money moves</span>
  <form method="post" action="{config.API_BASE_URL}/payments/sandbox/{txn_ref}/complete">
    <input type="hidden" name="result" value="success">
    <button class="pay" type="submit">Approve payment</button>
  </form>
  <form method="post" action="{config.API_BASE_URL}/payments/sandbox/{txn_ref}/complete">
    <input type="hidden" name="result" value="fail">
    <button class="fail" type="submit">Cancel</button>
  </form>
</div></body></html>"""
    return HTMLResponse(content=html)


@router.post("/sandbox/{txn_ref}/complete")
def sandbox_complete(
    txn_ref: str,
    result: str = Form("success"),
    db: Session = Depends(get_db),
):
    payment, ok, _ = simulate_sandbox(db, txn_ref, result == "success")
    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Unknown reference"
        )
    order = db.get(Order, payment.order_id)
    target = f"{config.FRONTEND_URL}/order/{order.id}?paid={'1' if ok else '0'}"
    return RedirectResponse(url=target, status_code=status.HTTP_303_SEE_OTHER)
