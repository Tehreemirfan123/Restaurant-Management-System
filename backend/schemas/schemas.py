from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from models.models import (
    CategoryEnum,
    OrderStatusEnum,
    PaymentMethodEnum,
    PaymentStatusEnum,
    RoleEnum,
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

    image_url: str | None = None

    available: bool | None = None


class MenuItemResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    price: Decimal
    category: CategoryEnum
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
    total_amount: Decimal
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
