from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


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
