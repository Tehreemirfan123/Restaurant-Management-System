import uuid
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Boolean, Enum, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base
from models.enums import CategoryEnum, DayOfWeekEnum


class MenuItem(Base):
    __tablename__ = "menu_items"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    category: Mapped[CategoryEnum] = mapped_column(
        Enum(CategoryEnum),
        nullable=False,
    )

    # The day this dish is served on the rotating weekly menu.
    # Null means it's available any day (e.g. advance-order specials).
    day_of_week: Mapped[DayOfWeekEnum | None] = mapped_column(
        Enum(DayOfWeekEnum),
        nullable=True,
    )

    # Per-order packaging (+ other flat) cost, used in contribution costing.
    packaging_cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0"),
        nullable=False,
    )

    image_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    available: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    order_items: Mapped[list["OrderItem"]] = relationship(
        back_populates="menu_item",
    )
