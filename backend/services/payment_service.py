from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.models.models import (
    Order,
    Payment,
    PaymentStatusEnum,
)
from backend.schemas.schemas import PaymentCreate


def create_payment(
    db: Session,
    payment_data: PaymentCreate,
) -> Payment:
    # Find the order
    order = db.get(
        Order,
        payment_data.order_id,
    )

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    # Check if the order already has a payment
    if order.payment is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order has already been paid",
        )

    # Create payment using the amount stored on the order
    payment = Payment(
        order_id=order.id,
        amount=order.total_amount,
        method=payment_data.method,
        status=PaymentStatusEnum.paid,
        paid_at=datetime.now(timezone.utc),
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment


def get_payment(
    db: Session,
    payment_id: UUID,
) -> Payment | None:
    return db.get(
        Payment,
        payment_id,
    )