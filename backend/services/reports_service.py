from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models.models import (
    InventoryItem,
    MenuItem,
    Order,
    OrderItem,
    Payment,
    PaymentStatusEnum,
)


def get_summary(db: Session) -> dict:
    today = datetime.now(timezone.utc).date()

    paid = Payment.status == PaymentStatusEnum.paid

    total_revenue = db.scalar(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(paid)
    )

    today_revenue = db.scalar(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            paid,
            func.date(Payment.paid_at) == today,
        )
    )

    total_orders = db.scalar(select(func.count(Order.id)))

    today_orders = db.scalar(
        select(func.count(Order.id)).where(
            func.date(Order.created_at) == today
        )
    )

    top_rows = db.execute(
        select(
            MenuItem.name,
            func.sum(OrderItem.quantity).label("qty"),
        )
        .join(OrderItem, OrderItem.menu_item_id == MenuItem.id)
        .group_by(MenuItem.name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(5)
    ).all()

    top_items = [
        {"name": name, "quantity": int(qty)} for name, qty in top_rows
    ]

    low_stock = list(
        db.scalars(
            select(InventoryItem)
            .where(InventoryItem.quantity <= InventoryItem.reorder_level)
            .order_by(InventoryItem.name)
        ).all()
    )

    return {
        "total_revenue": total_revenue,
        "today_revenue": today_revenue,
        "total_orders": total_orders,
        "today_orders": today_orders,
        "top_items": top_items,
        "low_stock": low_stock,
    }
