from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.config import DELIVERY_FEE
from models.models import (
    Customer,
    MenuItem,
    Order,
    OrderTypeEnum,
    OrderItem,
    Table,
)
from schemas.schemas import OrderCreate


def create_order(
    db: Session,
    order_data: OrderCreate,
) -> Order:
    menu_item_ids = [
        item.menu_item_id
        for item in order_data.items
    ]

    menu_items = db.scalars(
        select(MenuItem).where(
            MenuItem.id.in_(menu_item_ids)
        )
    ).all()

    menu_items_by_id = {
        menu_item.id: menu_item
        for menu_item in menu_items
    }

    if len(menu_items_by_id) != len(
        set(menu_item_ids)
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more menu items were not found",
        )

    # A dine-in order needs a table; validate any references that were given.
    if order_data.table_id is not None:
        table = db.get(Table, order_data.table_id)
        if table is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Table not found",
            )

    if (
        order_data.order_type == OrderTypeEnum.dine_in
        and order_data.table_id is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A dine-in order requires a table",
        )

    # A delivery order needs an address and carries the flat delivery fee.
    delivery_fee = Decimal("0")
    if order_data.order_type == OrderTypeEnum.delivery:
        if not order_data.delivery_address:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A delivery order requires a delivery address",
            )
        delivery_fee = DELIVERY_FEE

    # Resolve the customer: an explicit id, or find-or-create by phone so
    # repeat orders are tracked even for online checkouts.
    customer_id = order_data.customer_id

    if customer_id is not None:
        customer = db.get(Customer, customer_id)
        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found",
            )
    elif order_data.customer_phone:
        customer = db.scalar(
            select(Customer).where(
                Customer.phone == order_data.customer_phone
            )
        )
        if customer is None:
            customer = Customer(
                name=order_data.customer_name or "Customer",
                phone=order_data.customer_phone,
                address=order_data.delivery_address,
            )
            db.add(customer)
            db.flush()
        customer_id = customer.id

    order = Order(
        total_amount=0,
        order_type=order_data.order_type,
        delivery_fee=delivery_fee,
        delivery_address=order_data.delivery_address,
        table_id=order_data.table_id,
        customer_id=customer_id,
    )

    db.add(order)

    total_amount = 0

    for item_data in order_data.items:
        menu_item = menu_items_by_id[
            item_data.menu_item_id
        ]

        if not menu_item.available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"{menu_item.name} "
                    "is currently unavailable"
                ),
            )

        unit_price = menu_item.price

        subtotal = (
            unit_price * item_data.quantity
        )

        order_item = OrderItem(
            order=order,
            menu_item=menu_item,
            quantity=item_data.quantity,
            unit_price=unit_price,
        )

        db.add(order_item)

        total_amount += subtotal

    order.total_amount = total_amount + delivery_fee

    db.commit()
    db.refresh(order)

    return order


def get_orders(
    db: Session,
) -> list[Order]:
    return list(
        db.scalars(
            select(Order)
            .order_by(Order.created_at.desc())
        ).all()
    )


def get_order(
    db: Session,
    order_id: UUID,
) -> Order | None:
    return db.get(
        Order,
        order_id,
    )


def update_order_status(
    db: Session,
    order: Order,
    status_value,
) -> Order:
    order.status = status_value

    db.commit()
    db.refresh(order)

    return order