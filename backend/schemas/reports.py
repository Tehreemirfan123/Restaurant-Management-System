from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TopItem(BaseModel):
    name: str
    quantity: int


class LowStockItem(BaseModel):
    id: UUID
    name: str
    unit: str
    quantity: Decimal
    reorder_level: Decimal

    model_config = ConfigDict(from_attributes=True)


class ReportsSummary(BaseModel):
    total_revenue: Decimal
    today_revenue: Decimal
    total_orders: int
    today_orders: int
    # Customer / repeat metrics (business plan's primary KPI).
    total_customers: int
    repeat_customers: int
    second_order_rate: float
    total_waste_value: Decimal
    average_rating: float
    feedback_count: int
    top_items: list[TopItem]
    low_stock: list[LowStockItem]
    # Period-scoped metrics (period = today | week | month | all)
    period: str
    period_revenue: Decimal
    period_orders: int
    period_new_customers: int
    period_cost: Decimal
    period_profit: Decimal
    period_avg_order_value: Decimal
    period_waste_value: Decimal


class DishCosting(BaseModel):
    menu_item_id: UUID
    name: str
    price: Decimal
    ingredient_cost: Decimal
    packaging_cost: Decimal
    variable_cost: Decimal
    contribution: Decimal
    margin_percent: float
    has_recipe: bool
