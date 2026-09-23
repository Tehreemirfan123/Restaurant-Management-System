from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from models.enums import (
    OrderCategoryEnum,
    OrderStatusEnum,
    OrderTypeEnum,
    PaymentMethodEnum,
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
