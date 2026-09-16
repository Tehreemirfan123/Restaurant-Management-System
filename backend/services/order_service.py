from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from models.models import (
    MenuItem,
    Order,
    OrderItem,
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

    order = Order(
        total_amount=0,
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

    order.total_amount = total_amount

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