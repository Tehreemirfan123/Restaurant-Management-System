from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from models.models import (
    CategoryEnum,
    CustomerSegmentEnum,
    DayOfWeekEnum,
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

    # Required when order_type is delivery (validated in the service).
    delivery_address: str | None = None

    table_id: UUID | None = None

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
    status: OrderStatusEnum
    order_type: OrderTypeEnum
    total_amount: Decimal
    delivery_fee: Decimal
    delivery_address: str | None
    table_id: UUID | None
    customer_id: UUID | None
    created_at: datetime
    items: list[OrderItemResponse]

    model_config = ConfigDict(
        from_attributes=True,
    )


class OrderStatusUpdate(BaseModel):
    status: OrderStatusEnum

class PaymentCreate(BaseModel):
    order_id: UUID

    method: PaymentMethodEnum


class PaymentResponse(BaseModel):
    id: UUID
    order_id: UUID
    amount: Decimal
    method: PaymentMethodEnum
    status: PaymentStatusEnum
    paid_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True,
    )

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
    top_items: list[TopItem]
    low_stock: list[LowStockItem]


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
