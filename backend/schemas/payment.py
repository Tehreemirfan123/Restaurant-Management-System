from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from models.enums import PaymentMethodEnum, PaymentStatusEnum


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


class CheckoutRequest(BaseModel):
    order_id: UUID
    method: PaymentMethodEnum


class CheckoutResponse(BaseModel):
    provider: str
    http_method: str
    checkout_url: str
    fields: dict[str, str]
    transaction_ref: str
    amount: Decimal


class CheckoutStatus(BaseModel):
    transaction_ref: str
    status: PaymentStatusEnum
    order_id: UUID
    amount: Decimal


class PaymentResponse(BaseModel):
    id: UUID
    order_id: UUID
    amount: Decimal
    method: PaymentMethodEnum
    status: PaymentStatusEnum
    reference: str | None = None
    note: str | None = None
    transaction_ref: str | None = None
    gateway: str | None = None
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
