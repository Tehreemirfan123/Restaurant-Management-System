from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


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
