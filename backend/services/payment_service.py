from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from models.models import (
    Order,
    Payment,
    PaymentStatusEnum,
    Staff,
)
from schemas.schemas import PaymentCreate, PaymentUpdate


def _paid_total(order: Order) -> Decimal:
    return sum(
        (p.amount for p in order.payments if p.status == PaymentStatusEnum.paid),
        Decimal("0"),
    )


def _annotate(payment: Payment) -> Payment:
    """Attach order number / customer / recorder for reconciliation views."""
    order = payment.order
    payment.order_number = order.order_number if order else None
    payment.customer_name = (
        order.customer.name if order and order.customer else None
    )
    payment.recorded_by = (
        payment.recorder.full_name if payment.recorder else None
    )
    return payment


def create_payment(
    db: Session,
    payment_data: PaymentCreate,
    recorded_by: Staff | None = None,
) -> Payment:
    order = db.get(Order, payment_data.order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    already_paid = _paid_total(order)
    balance = Decimal(order.total_amount or 0) - already_paid

    # Use the given amount for a partial/advance payment, otherwise the
    # outstanding balance.
    amount = (
        payment_data.amount
        if payment_data.amount is not None
        else balance
    )

    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This order is already fully paid",
        )

    # Never let recorded payments exceed the order total (small rounding slack).
    if amount - balance > Decimal("0.01"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Amount exceeds the outstanding balance of Rs. {balance:.0f}"
            ),
        )

    payment = Payment(
        order_id=order.id,
        amount=amount,
        method=payment_data.method,
        status=PaymentStatusEnum.paid,
        reference=payment_data.reference,
        note=payment_data.note,
        recorded_by_id=recorded_by.id if recorded_by else None,
        paid_at=datetime.now(timezone.utc),
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return _annotate(payment)


def update_payment(
    db: Session,
    payment: Payment,
    data: PaymentUpdate,
    recorded_by: Staff | None = None,
) -> Payment:
    """Confirm or adjust a payment (e.g. mark a pending intent as received)."""
    updates = data.model_dump(exclude_unset=True)

    if "reference" in updates:
        payment.reference = updates["reference"]
    if "note" in updates:
        payment.note = updates["note"]

    if "status" in updates and updates["status"] is not None:
        new_status = updates["status"]
        # Guard against confirming an amount that would overpay the order.
        if (
            new_status == PaymentStatusEnum.paid
            and payment.status != PaymentStatusEnum.paid
        ):
            order = payment.order
            balance = Decimal(order.total_amount or 0) - _paid_total(order)
            if payment.amount - balance > Decimal("0.01"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Confirming this payment would exceed the "
                        f"outstanding balance of Rs. {balance:.0f}"
                    ),
                )
            payment.paid_at = datetime.now(timezone.utc)
            if recorded_by is not None:
                payment.recorded_by_id = recorded_by.id
        payment.status = new_status

    db.commit()
    db.refresh(payment)
    return _annotate(payment)


def get_payment(
    db: Session,
    payment_id: UUID,
) -> Payment | None:
    payment = db.get(Payment, payment_id)
    return _annotate(payment) if payment is not None else None


def list_payments(
    db: Session,
    on_date: date | None = None,
    order_id: UUID | None = None,
) -> list[Payment]:
    query = (
        select(Payment)
        .options(
            selectinload(Payment.order).selectinload(Order.customer),
            selectinload(Payment.recorder),
        )
        .order_by(Payment.created_at.desc())
    )
    if order_id is not None:
        query = query.where(Payment.order_id == order_id)
    if on_date is not None:
        query = query.where(func.date(Payment.created_at) == on_date)

    payments = db.scalars(query).all()
    return [_annotate(p) for p in payments]


def reconciliation(db: Session, on_date: date) -> dict:
    """Daily reconciliation: settled payments + orders with a balance."""
    # Settled payments recorded on the given day.
    paid_query = (
        select(Payment)
        .options(
            selectinload(Payment.order).selectinload(Order.customer),
            selectinload(Payment.recorder),
        )
        .where(
            Payment.status == PaymentStatusEnum.paid,
            func.date(Payment.paid_at) == on_date,
        )
        .order_by(Payment.paid_at.desc())
    )
    payments = [_annotate(p) for p in db.scalars(paid_query).all()]

    by_method: dict = {}
    total = Decimal("0")
    for p in payments:
        total += p.amount
        row = by_method.setdefault(
            p.method, {"method": p.method, "count": 0, "amount": Decimal("0")}
        )
        row["count"] += 1
        row["amount"] += p.amount

    # Active orders that still carry a balance (unpaid or partially paid).
    from models.models import OrderStatusEnum

    orders = db.scalars(
        select(Order)
        .options(
            selectinload(Order.payments), selectinload(Order.customer)
        )
        .where(Order.status != OrderStatusEnum.cancelled)
        .order_by(Order.created_at.desc())
    ).all()

    settings = None
    outstanding = []
    for order in orders:
        paid = _paid_total(order)
        balance = Decimal(order.total_amount or 0) - paid
        if balance <= Decimal("0.01"):
            continue
        if settings is None:
            from services.settings_service import get_settings

            settings = get_settings(db)
        from services.order_service import compute_advance

        required, advance = compute_advance(
            order.total_amount, order.category, settings
        )
        outstanding.append(
            {
                "order_id": order.id,
                "order_number": order.order_number,
                "customer_name": (
                    order.customer.name if order.customer else None
                ),
                "total_amount": order.total_amount,
                "amount_paid": paid,
                "balance_due": balance,
                "advance_required": required,
                "advance_amount": advance,
            }
        )

    return {
        "date": on_date.isoformat(),
        "total_collected": total,
        "payment_count": len(payments),
        "by_method": list(by_method.values()),
        "payments": payments,
        "outstanding": outstanding,
    }
