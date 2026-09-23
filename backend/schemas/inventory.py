from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


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
