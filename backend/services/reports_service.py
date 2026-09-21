from datetime import timedelta

from core.config import local_today

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from decimal import Decimal

from models.models import (
    Customer,
    InventoryItem,
    Order,
    OrderItem,
    OrderStatusEnum,
    MenuItem,
    Payment,
    PaymentStatusEnum,
    Recipe,
    RecipeIngredient,
    WasteLog,
)


def _period_start(period: str):
    """Start date (inclusive) for a reporting period, or None for all-time."""
    today = local_today()
    if period == "today":
        return today
    if period == "week":
        return today - timedelta(days=6)
    if period == "month":
        return today - timedelta(days=29)
    return None


def _period_metrics(db: Session, period: str) -> dict:
    start = _period_start(period)
    not_cancelled = Order.status != OrderStatusEnum.cancelled
    paid = Payment.status == PaymentStatusEnum.paid

    rev_q = select(func.coalesce(func.sum(Payment.amount), 0)).where(paid)
    ord_q = select(func.count(Order.id)).where(not_cancelled)
    cust_q = select(func.count(Customer.id))
    if start is not None:
        rev_q = rev_q.where(func.date(Payment.paid_at) >= start)
        ord_q = ord_q.where(func.date(Order.created_at) >= start)
        cust_q = cust_q.where(func.date(Customer.created_at) >= start)

    revenue = db.scalar(rev_q) or Decimal("0")
    orders = db.scalar(ord_q) or 0
    new_customers = db.scalar(cust_q) or 0

    # Estimated cost of goods for orders placed in the period.
    varcost = {
        c["menu_item_id"]: c["variable_cost"] for c in get_costing(db)
    }
    oi_q = (
        select(OrderItem.menu_item_id, OrderItem.quantity)
        .join(Order, Order.id == OrderItem.order_id)
        .where(not_cancelled)
    )
    if start is not None:
        oi_q = oi_q.where(func.date(Order.created_at) >= start)
    cost = Decimal("0")
    for mid, qty in db.execute(oi_q).all():
        cost += Decimal(varcost.get(mid, 0)) * qty

    # Waste value in the period (only for costed inventory items).
    w_q = select(WasteLog.quantity, InventoryItem.unit_cost).join(
        InventoryItem, InventoryItem.id == WasteLog.inventory_item_id
    )
    if start is not None:
        w_q = w_q.where(func.date(WasteLog.created_at) >= start)
    waste = Decimal("0")
    for qty, unit_cost in db.execute(w_q).all():
        waste += (qty or Decimal("0")) * (unit_cost or Decimal("0"))

    avg_order_value = (
        (revenue / orders) if orders else Decimal("0")
    )

    return {
        "period": period,
        "period_revenue": revenue,
        "period_orders": orders,
        "period_new_customers": new_customers,
        "period_cost": cost,
        "period_profit": revenue - cost,
        "period_avg_order_value": avg_order_value,
        "period_waste_value": waste,
    }


def get_summary(db: Session, period: str = "all") -> dict:
    today = local_today()

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

    # Repeat-customer metrics: count orders per (known) customer.
    per_customer = (
        select(
            Order.customer_id,
            func.count(Order.id).label("cnt"),
        )
        .where(Order.customer_id.is_not(None))
        .group_by(Order.customer_id)
        .subquery()
    )

    total_customers = db.scalar(
        select(func.count()).select_from(per_customer)
    ) or 0

    repeat_customers = db.scalar(
        select(func.count())
        .select_from(per_customer)
        .where(per_customer.c.cnt >= 2)
    ) or 0

    second_order_rate = (
        round(repeat_customers / total_customers * 100, 1)
        if total_customers
        else 0.0
    )

    from models.models import OrderFeedback
    from services.waste_service import total_waste_value

    feedback_count = db.scalar(
        select(func.count(OrderFeedback.id))
    ) or 0
    avg_rating = db.scalar(
        select(func.avg(OrderFeedback.rating))
    )
    average_rating = round(float(avg_rating), 1) if avg_rating else 0.0

    result = {
        "total_revenue": total_revenue,
        "today_revenue": today_revenue,
        "total_orders": total_orders,
        "today_orders": today_orders,
        "total_customers": total_customers,
        "repeat_customers": repeat_customers,
        "second_order_rate": second_order_rate,
        "total_waste_value": total_waste_value(db),
        "average_rating": average_rating,
        "feedback_count": feedback_count,
        "top_items": top_items,
        "low_stock": low_stock,
    }
    result.update(_period_metrics(db, period))
    return result


def get_costing(db: Session) -> list[dict]:
    """Per-dish variable cost and contribution.

    ingredient cost (from the recipe x inventory unit costs) + packaging cost
    = variable cost; price - variable cost = contribution.
    """
    # Ingredient cost per recipe's menu item.
    rows = db.execute(
        select(
            Recipe.menu_item_id,
            func.coalesce(
                func.sum(RecipeIngredient.quantity * InventoryItem.unit_cost),
                0,
            ),
        )
        .join(RecipeIngredient, RecipeIngredient.recipe_id == Recipe.id)
        .join(
            InventoryItem,
            InventoryItem.id == RecipeIngredient.inventory_item_id,
        )
        .group_by(Recipe.menu_item_id)
    ).all()
    ingredient_cost_by_item = {mid: cost for mid, cost in rows}

    recipe_item_ids = set(
        db.scalars(select(Recipe.menu_item_id)).all()
    )

    menu_items = db.scalars(
        select(MenuItem).order_by(MenuItem.name)
    ).all()

    result = []
    for item in menu_items:
        ingredient_cost = Decimal(
            ingredient_cost_by_item.get(item.id, 0)
        )
        packaging_cost = item.packaging_cost or Decimal("0")
        variable_cost = ingredient_cost + packaging_cost
        contribution = item.price - variable_cost
        margin = (
            round(float(contribution / item.price) * 100, 1)
            if item.price
            else 0.0
        )
        result.append(
            {
                "menu_item_id": item.id,
                "name": item.name,
                "price": item.price,
                "ingredient_cost": ingredient_cost,
                "packaging_cost": packaging_cost,
                "variable_cost": variable_cost,
                "contribution": contribution,
                "margin_percent": margin,
                "has_recipe": item.id in recipe_item_ids,
            }
        )
    return result
