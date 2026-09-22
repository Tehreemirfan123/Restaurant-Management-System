from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from models.models import (
    CategoryEnum,
    CustomerSegmentEnum,
    DayOfWeekEnum,
    OrderCategoryEnum,
    OrderStatusEnum,
    OrderTypeEnum,
    PaymentMethodEnum,
    PaymentStatusEnum,
    RoleEnum,
    TableStatusEnum,
)

class MenuItemCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=150,
    )

    description: str | None = None

    price: Decimal = Field(
        gt=0,
        decimal_places=2,
    )

    category: CategoryEnum

    day_of_week: DayOfWeekEnum | None = None

    packaging_cost: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)

    image_url: str | None = None

    available: bool = True


class MenuItemUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    description: str | None = None

    price: Decimal | None = Field(
        default=None,
        gt=0,
        decimal_places=2,
    )

    category: CategoryEnum | None = None

    day_of_week: DayOfWeekEnum | None = None

    packaging_cost: Decimal | None = Field(default=None, ge=0, decimal_places=2)

    image_url: str | None = None

    available: bool | None = None


class MenuItemResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    price: Decimal
    category: CategoryEnum
    day_of_week: DayOfWeekEnum | None
    packaging_cost: Decimal
    image_url: str | None
    available: bool

    model_config = ConfigDict(
        from_attributes=True,
    )


class OrderItemCreate(BaseModel):
    menu_item_id: UUID
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    items: list[OrderItemCreate] = Field(
        min_length=1,
    )

    order_type: OrderTypeEnum = OrderTypeEnum.pickup

    # Regular / custom / subscription / large — drives the advance rule.
    category: OrderCategoryEnum = OrderCategoryEnum.regular

    # Required when order_type is delivery (validated in the service).
    delivery_address: str | None = None
    # Distance from the kitchen (km); drives the delivery fee.
    delivery_distance_km: Decimal | None = Field(
        default=None, ge=0, decimal_places=1
    )

    table_id: UUID | None = None

    # Optional intended payment method. When given, a pending payment is
    # recorded so it shows up in reconciliation until it is confirmed.
    payment_method: PaymentMethodEnum | None = None

    # Either link an existing customer, or pass name/phone to find-or-create
    # one so repeat orders can be tracked.
    customer_id: UUID | None = None
    customer_name: str | None = None
    customer_phone: str | None = None


class OrderItemResponse(BaseModel):
    id: UUID
    menu_item_id: UUID
    quantity: int
    unit_price: Decimal

    model_config = ConfigDict(
        from_attributes=True,
    )


class OrderResponse(BaseModel):
    id: UUID
    order_number: int
    status: OrderStatusEnum
    order_type: OrderTypeEnum
    category: OrderCategoryEnum
    total_amount: Decimal
    delivery_fee: Decimal
    delivery_address: str | None
    delivery_distance_km: Decimal | None
    table_id: UUID | None
    customer_id: UUID | None
    created_at: datetime
    items: list[OrderItemResponse]
    # Convenience fields for the orders view (set on the ORM object).
    customer_name: str | None = None
    payment_status: str | None = None
    # Payment roll-up (computed in the service).
    amount_paid: Decimal = Decimal("0")
    balance_due: Decimal = Decimal("0")
    advance_required: bool = False
    advance_amount: Decimal = Decimal("0")

    model_config = ConfigDict(
        from_attributes=True,
    )


class OrderStatusUpdate(BaseModel):
    status: OrderStatusEnum

class PaymentCreate(BaseModel):
    order_id: UUID

    method: PaymentMethodEnum

    # Optional partial/advance amount; defaults to the outstanding balance.
    amount: Decimal | None = Field(default=None, gt=0, decimal_places=2)

    # External transaction reference (bank/JazzCash/Easypaisa id, cheque no.).
    reference: str | None = Field(default=None, max_length=120)
    note: str | None = None


class PaymentUpdate(BaseModel):
    """Confirm or adjust a recorded payment during reconciliation."""

    status: PaymentStatusEnum | None = None
    reference: str | None = Field(default=None, max_length=120)
    note: str | None = None


class PaymentResponse(BaseModel):
    id: UUID
    order_id: UUID
    amount: Decimal
    method: PaymentMethodEnum
    status: PaymentStatusEnum
    reference: str | None = None
    note: str | None = None
    created_at: datetime | None = None
    paid_at: datetime | None
    # Reconciliation convenience fields (set on the ORM object).
    order_number: int | None = None
    customer_name: str | None = None
    recorded_by: str | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class MethodTotal(BaseModel):
    method: PaymentMethodEnum
    count: int
    amount: Decimal


class OutstandingOrder(BaseModel):
    order_id: UUID
    order_number: int
    customer_name: str | None
    total_amount: Decimal
    amount_paid: Decimal
    balance_due: Decimal
    advance_required: bool
    advance_amount: Decimal


class PaymentReconciliation(BaseModel):
    date: str
    total_collected: Decimal
    payment_count: int
    by_method: list[MethodTotal]
    payments: list[PaymentResponse]
    outstanding: list[OutstandingOrder]

class StaffCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=100,
    )

    full_name: str = Field(
        min_length=1,
        max_length=150,
    )

    password: str = Field(
        min_length=6,
        max_length=128,
    )

    role: RoleEnum = RoleEnum.staff


class StaffResponse(BaseModel):
    id: UUID
    username: str
    full_name: str
    role: RoleEnum
    active: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: RoleEnum
    full_name: str


# ---- Customers ----

class CustomerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    phone: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=255)
    address: str | None = None
    segment: CustomerSegmentEnum | None = None


class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    phone: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=255)
    address: str | None = None
    segment: CustomerSegmentEnum | None = None


class CustomerResponse(BaseModel):
    id: UUID
    name: str
    phone: str | None
    email: str | None
    address: str | None
    segment: CustomerSegmentEnum | None
    created_at: datetime
    # Derived stats (default so a plain ORM object still validates).
    order_count: int = 0
    last_order_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# ---- Tables ----

class TableCreate(BaseModel):
    number: int = Field(gt=0)
    capacity: int = Field(gt=0)
    status: TableStatusEnum = TableStatusEnum.available


class TableUpdate(BaseModel):
    number: int | None = Field(default=None, gt=0)
    capacity: int | None = Field(default=None, gt=0)
    status: TableStatusEnum | None = None


class TableResponse(BaseModel):
    id: UUID
    number: int
    capacity: int
    status: TableStatusEnum

    model_config = ConfigDict(from_attributes=True)


# ---- Inventory ----

class InventoryItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    unit: str = Field(min_length=1, max_length=30)
    quantity: Decimal = Field(ge=0, decimal_places=3)
    reorder_level: Decimal = Field(
        default=Decimal("0"), ge=0, decimal_places=3
    )
    unit_cost: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    supplier: str | None = Field(default=None, max_length=150)


class InventoryItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    unit: str | None = Field(default=None, min_length=1, max_length=30)
    quantity: Decimal | None = Field(default=None, ge=0, decimal_places=3)
    reorder_level: Decimal | None = Field(default=None, ge=0, decimal_places=3)
    unit_cost: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    supplier: str | None = Field(default=None, max_length=150)


class InventoryItemResponse(BaseModel):
    id: UUID
    name: str
    unit: str
    quantity: Decimal
    reorder_level: Decimal
    unit_cost: Decimal
    supplier: str | None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---- Waste ----

class WasteLogCreate(BaseModel):
    inventory_item_id: UUID | None = None
    description: str | None = None
    quantity: Decimal = Field(gt=0, decimal_places=3)


class WasteLogResponse(BaseModel):
    id: UUID
    inventory_item_id: UUID | None
    item_name: str | None = None
    description: str | None
    quantity: Decimal
    cost: Decimal = Decimal("0")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---- Recipes ----

class RecipeIngredientCreate(BaseModel):
    inventory_item_id: UUID
    quantity: Decimal = Field(gt=0, decimal_places=3)


class RecipeCreate(BaseModel):
    menu_item_id: UUID
    notes: str | None = None
    ingredients: list[RecipeIngredientCreate] = Field(default_factory=list)


class RecipeUpdate(BaseModel):
    notes: str | None = None
    ingredients: list[RecipeIngredientCreate] | None = None


class RecipeIngredientResponse(BaseModel):
    id: UUID
    inventory_item_id: UUID
    quantity: Decimal

    model_config = ConfigDict(from_attributes=True)


class RecipeResponse(BaseModel):
    id: UUID
    menu_item_id: UUID
    notes: str | None
    ingredients: list[RecipeIngredientResponse]

    model_config = ConfigDict(from_attributes=True)


# ---- Reports ----

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


# ---- Feedback ----

class FeedbackCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    would_reorder: bool = True
    comment: str | None = None


class FeedbackResponse(BaseModel):
    id: UUID
    order_id: UUID
    rating: int
    would_reorder: bool
    comment: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---- Settings ----

class SettingsUpdate(BaseModel):
    accepting_orders: bool | None = None
    daily_order_cap: int | None = Field(default=None, ge=0)
    restaurant_name: str | None = Field(default=None, min_length=1, max_length=150)
    contact_phone: str | None = Field(default=None, max_length=30)
    address: str | None = None
    opening_hours: str | None = Field(default=None, max_length=120)
    delivery_fee: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    delivery_radius_km: Decimal | None = Field(default=None, ge=0, decimal_places=1)
    # Changes in delivery charges in the code
    delivery_per_km: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    # Payment configuration.
    advance_payment_percent: Decimal | None = Field(
        default=None, ge=0, le=100, decimal_places=2
    )
    large_order_threshold: Decimal | None = Field(
        default=None, ge=0, decimal_places=2
    )
    bank_name: str | None = Field(default=None, max_length=120)
    bank_account_name: str | None = Field(default=None, max_length=150)
    bank_account_number: str | None = Field(default=None, max_length=60)
    jazzcash_number: str | None = Field(default=None, max_length=30)
    easypaisa_number: str | None = Field(default=None, max_length=30)


class SettingsResponse(BaseModel):
    accepting_orders: bool
    daily_order_cap: int | None
    restaurant_name: str
    contact_phone: str | None
    address: str | None
    opening_hours: str | None
    delivery_fee: Decimal
    delivery_radius_km: Decimal
    delivery_per_km: Decimal
    advance_payment_percent: Decimal
    large_order_threshold: Decimal
    bank_name: str | None
    bank_account_name: str | None
    bank_account_number: str | None
    jazzcash_number: str | None
    easypaisa_number: str | None

    model_config = ConfigDict(from_attributes=True)


class OrderingStatus(BaseModel):
    accepting_orders: bool
    orders_today: int
    daily_order_cap: int | None
    delivery_fee: Decimal
    # Public business info for the customer website.
    restaurant_name: str
    contact_phone: str | None
    address: str | None
    opening_hours: str | None
    delivery_radius_km: Decimal
    # Changes in delivery charges in the code
    delivery_per_km: Decimal
    # Public payment info so the cart can show the advance rule + accounts.
    advance_payment_percent: Decimal
    large_order_threshold: Decimal
    bank_name: str | None
    bank_account_name: str | None
    bank_account_number: str | None
    jazzcash_number: str | None
    easypaisa_number: str | None
