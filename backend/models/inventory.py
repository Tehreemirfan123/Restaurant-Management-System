import uuid
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        unique=True,
    )

    unit: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 3),
        default=Decimal("0"),
        nullable=False,
    )

    reorder_level: Mapped[Decimal] = mapped_column(
        Numeric(10, 3),
        default=Decimal("0"),
        nullable=False,
    )

    # Cost per unit (Rs. per kg/litre/piece), used for dish costing.
    unit_cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0"),
        nullable=False,
    )

    supplier: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    recipe_ingredients: Mapped[list["RecipeIngredient"]] = relationship(
        back_populates="inventory_item",
    )


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    menu_item_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("menu_items.id"),
        nullable=False,
        unique=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    menu_item: Mapped["MenuItem"] = relationship()

    ingredients: Mapped[list["RecipeIngredient"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
    )


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    recipe_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("recipes.id"),
        nullable=False,
    )

    inventory_item_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("inventory_items.id"),
        nullable=False,
    )

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 3),
        nullable=False,
    )

    recipe: Mapped["Recipe"] = relationship(
        back_populates="ingredients",
    )

    inventory_item: Mapped["InventoryItem"] = relationship(
        back_populates="recipe_ingredients",
    )


class WasteLog(Base):
    __tablename__ = "waste_logs"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    inventory_item_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("inventory_items.id"),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 3),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    inventory_item: Mapped["InventoryItem | None"] = relationship()
