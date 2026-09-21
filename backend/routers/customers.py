from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_staff
from models.models import Staff
from schemas.schemas import (
    CustomerCreate,
    CustomerResponse,
    CustomerUpdate,
)
from services.customer_service import (
    create_customer,
    delete_customer,
    get_customer,
    list_customers_with_stats,
    update_customer,
)


router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
    dependencies=[Depends(get_current_staff)],
)


@router.get("", response_model=list[CustomerResponse])
def read_customers(db: Session = Depends(get_db)):
    return list_customers_with_stats(db)


@router.get("/{customer_id}", response_model=CustomerResponse)
def read_customer(customer_id: UUID, db: Session = Depends(get_db)):
    customer = get_customer(db, customer_id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    return customer


@router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
):
    return create_customer(db, customer_data)


@router.put("/{customer_id}", response_model=CustomerResponse)
def edit_customer(
    customer_id: UUID,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db),
):
    customer = get_customer(db, customer_id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    return update_customer(db, customer, customer_data)


@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_customer(customer_id: UUID, db: Session = Depends(get_db)):
    customer = get_customer(db, customer_id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    delete_customer(db, customer)
