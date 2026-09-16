from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.schemas.schemas import (
    PaymentCreate,
    PaymentResponse,
)
from backend.services.payment_service import (
    create_payment,
    get_payment,
)


router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


@router.post(
    "",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
):
    return create_payment(
        db,
        payment_data,
    )


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
)
def read_payment(
    payment_id: UUID,
    db: Session = Depends(get_db),
):
    payment = get_payment(
        db,
        payment_id,
    )

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    return payment