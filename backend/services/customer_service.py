from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models.models import Customer, Order
from schemas.schemas import CustomerCreate, CustomerUpdate


def get_customers(db: Session) -> list[Customer]:
    return list(
        db.scalars(
            select(Customer).order_by(Customer.name)
        ).all()
    )


def list_customers_with_stats(db: Session) -> list[dict]:
    """Customers with derived order_count and last_order_at for the CRM view."""
    rows = db.execute(
        select(
            Customer,
            func.count(Order.id).label("order_count"),
            func.max(Order.created_at).label("last_order_at"),
        )
        .outerjoin(Order, Order.customer_id == Customer.id)
        .group_by(Customer.id)
        .order_by(func.max(Order.created_at).desc().nullslast())
    ).all()

    result = []
    for customer, order_count, last_order_at in rows:
        result.append(
            {
                "id": customer.id,
                "name": customer.name,
                "phone": customer.phone,
                "email": customer.email,
                "address": customer.address,
                "segment": customer.segment,
                "created_at": customer.created_at,
                "order_count": int(order_count or 0),
                "last_order_at": last_order_at,
            }
        )
    return result


def get_customer_by_phone(
    db: Session,
    phone: str,
) -> Customer | None:
    return db.scalar(
        select(Customer).where(Customer.phone == phone)
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
