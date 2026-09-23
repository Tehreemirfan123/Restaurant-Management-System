import uuid
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Identity,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base
from models.enums import OrderCategoryEnum, OrderStatusEnum, OrderTypeEnum


class Order(Base):
    __tablename__ = "orders"
    # Uniqueness is a named constraint (matches the migration); the column
    # also carries a plain index for lookups.
    __table_args__ = (
        UniqueConstraint("order_number", name="uq_orders_order_number"),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Human-friendly sequential number used on receipts and for payment
    # reconciliation ("Order #1042"). The UUID id stays the internal key.
    order_number: Mapped[int] = mapped_column(
        Integer,
        Identity(start=1001),
        nullable=False,
        index=True,
    )

    status: Mapped[OrderStatusEnum] = mapped_column(
        Enum(OrderStatusEnum),
        default=OrderStatusEnum.received,
        nullable=False,
    )

    order_type: Mapped[OrderTypeEnum] = mapped_column(
        Enum(OrderTypeEnum),
        default=OrderTypeEnum.pickup,
        nullable=False,
    )

    # Drives the advance-payment rule (see settings.advance_payment_percent).
    category: Mapped[OrderCategoryEnum] = mapped_column(
        Enum(OrderCategoryEnum),
        default=OrderCategoryEnum.regular,
        nullable=False,
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    delivery_fee: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0"),
        nullable=False,
    )

    delivery_address: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Distance used to calculate the delivery fee (km).
    delivery_distance_km: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 1),
        nullable=True,
    )

    table_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("tables.id"),
        nullable=True,
    )

    customer_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("customers.id"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )

    # An order can have several payments recorded against it (e.g. a 50%
    # advance followed by the balance on delivery).
    payments: Mapped[list["Payment"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        order_by="Payment.created_at",
    )

    table: Mapped["Table | None"] = relationship(
        back_populates="orders",
    )

    customer: Mapped["Customer | None"] = relationship(
        back_populates="orders",
    )

    feedback: Mapped["OrderFeedback | None"] = relationship(
        back_populates="order",
        uselist=False,
        cascade="all, delete-orphan",
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    quantity: Mapped[int] = mapped_column(
        nullable=False,
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    order_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("orders.id"),
        nullable=False,
    )

    menu_item_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("menu_items.id"),
        nullable=False,
    )

    order: Mapped["Order"] = relationship(
        back_populates="items",
    )

    menu_item: Mapped["MenuItem"] = relationship(
        back_populates="order_items",
    )


class OrderFeedback(Base):
    __tablename__ = "order_feedback"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    order_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("orders.id"),
        nullable=False,
        unique=True,
    )

    rating: Mapped[int] = mapped_column(
        nullable=False,
    )

    would_reorder: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    order: Mapped["Order"] = relationship(
        back_populates="feedback",
    )
