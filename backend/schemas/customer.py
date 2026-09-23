from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from models.enums import CustomerSegmentEnum


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
