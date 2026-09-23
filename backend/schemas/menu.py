from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from models.enums import CategoryEnum, DayOfWeekEnum


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
