import uuid
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from database.database import Base


class Settings(Base):
    __tablename__ = "settings"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Master switch to stop taking orders when at capacity / closed.
    accepting_orders: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Max orders accepted per day (null = no limit). Pilot starts at ~5.
    daily_order_cap: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    # Business info (shown to customers / used on receipts).
    restaurant_name: Mapped[str] = mapped_column(
        String(150),
        default="Mehak's Kitchen",
        nullable=False,
    )

    contact_phone: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    address: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    opening_hours: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    # Delivery configuration.
    delivery_fee: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("80"),
        nullable=False,
    )

    delivery_radius_km: Mapped[Decimal] = mapped_column(
        Numeric(5, 1),
        default=Decimal("3"),
        nullable=False,
    )

    # Extra charge per km beyond the base delivery radius.
    # Changes in delivery charges in the code
    delivery_per_km: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("26"),
        nullable=False,
    )

    # --- Payments (configurable so requirements can change later) ---
    # Advance required (%) for custom / subscription / large orders.
    advance_payment_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("50"),
        nullable=False,
    )

    # Orders at or above this total require an advance regardless of category.
    large_order_threshold: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("3000"),
        nullable=False,
    )

    # Payment account details shown to customers for bank transfer / wallets.
    bank_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    bank_account_name: Mapped[str | None] = mapped_column(
        String(150), nullable=True
    )
    bank_account_number: Mapped[str | None] = mapped_column(
        String(60), nullable=True
    )
    jazzcash_number: Mapped[str | None] = mapped_column(
        String(30), nullable=True
    )
    easypaisa_number: Mapped[str | None] = mapped_column(
        String(30), nullable=True
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
