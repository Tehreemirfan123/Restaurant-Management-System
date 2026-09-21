from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from decimal import Decimal

from models.models import (
    InventoryItem,
    MenuItem,
    Order,
    OrderItem,
    Payment,
    PaymentStatusEnum,
    Recipe,
    RecipeIngredient,
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

    return {
        "total_revenue": total_revenue,
        "today_revenue": today_revenue,
        "total_orders": total_orders,
        "today_orders": today_orders,
        "total_customers": total_customers,
        "repeat_customers": repeat_customers,
        "second_order_rate": second_order_rate,
        "top_items": top_items,
        "low_stock": low_stock,
    }


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
