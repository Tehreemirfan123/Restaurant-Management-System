from datetime import date as date_cls
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.config import local_today
from database.database import get_db
from dependencies.auth import get_current_staff
from models.models import Payment, Staff
from schemas.schemas import (
    PaymentCreate,
    PaymentReconciliation,
    PaymentResponse,
    PaymentUpdate,
)
from services.payment_service import (
    create_payment,
    get_payment,
    list_payments,
    reconciliation,
    update_payment,
)


router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
    dependencies=[Depends(get_current_staff)],
)


@router.post(
    "",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    staff: Staff = Depends(get_current_staff),
):
    return create_payment(db, payment_data, recorded_by=staff)


@router.get(
    "",
    response_model=list[PaymentResponse],
)
def read_payments(
    db: Session = Depends(get_db),
    on_date: date_cls | None = Query(default=None, alias="date"),
    order_id: UUID | None = Query(default=None),
):
    return list_payments(db, on_date=on_date, order_id=order_id)


@router.get(
    "/reconciliation",
    response_model=PaymentReconciliation,
)
def daily_reconciliation(
    db: Session = Depends(get_db),
    on_date: date_cls | None = Query(default=None, alias="date"),
):
    return reconciliation(db, on_date or local_today())


@router.patch(
    "/{payment_id}",
    response_model=PaymentResponse,
)
def edit_payment(
    payment_id: UUID,
    data: PaymentUpdate,
    db: Session = Depends(get_db),
    staff: Staff = Depends(get_current_staff),
):
    payment = db.get(Payment, payment_id)
    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )
    return update_payment(db, payment, data, recorded_by=staff)


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
)
def read_payment(
    payment_id: UUID,
    db: Session = Depends(get_db),
):
    payment = get_payment(db, payment_id)

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    return payment
