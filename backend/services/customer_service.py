from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.models import Customer
from schemas.schemas import CustomerCreate, CustomerUpdate


def get_customers(db: Session) -> list[Customer]:
    return list(
        db.scalars(
            select(Customer).order_by(Customer.name)
        ).all()
    )


def get_customer(db: Session, customer_id: UUID) -> Customer | None:
    return db.get(Customer, customer_id)


def create_customer(
    db: Session,
    customer_data: CustomerCreate,
) -> Customer:
    customer = Customer(**customer_data.model_dump())

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return customer


def update_customer(
    db: Session,
    customer: Customer,
    customer_data: CustomerUpdate,
) -> Customer:
    updates = customer_data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)

    return customer


def delete_customer(db: Session, customer: Customer) -> None:
    db.delete(customer)
    db.commit()
