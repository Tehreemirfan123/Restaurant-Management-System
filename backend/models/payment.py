import uuid
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base
from models.enums import PaymentMethodEnum, PaymentStatusEnum


class Payment(Base):
    __tablename__ = "payments"
    # Uniqueness is a named constraint (matches the migration); the column
    # also carries a plain index for callback lookups.
    __table_args__ = (
        UniqueConstraint(
            "transaction_ref", name="uq_payments_transaction_ref"
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    order_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("orders.id"),
        nullable=False,
        index=True,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    method: Mapped[PaymentMethodEnum] = mapped_column(
        Enum(PaymentMethodEnum),
        nullable=False,
    )

    status: Mapped[PaymentStatusEnum] = mapped_column(
        Enum(PaymentStatusEnum),
        default=PaymentStatusEnum.pending,
        nullable=False,
    )

    # External reference (bank/JazzCash/Easypaisa transaction id, cheque no.)
    # captured during reconciliation or returned by the payment gateway.
    reference: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    # Our own unique reference for a gateway checkout attempt (sent to the
    # gateway and echoed back in its callback so we can match the payment).
    transaction_ref: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )

    # Which gateway processed this payment (sandbox / jazzcash / easypaisa),
    # or null for a manually recorded payment.
    gateway: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Staff member who recorded/confirmed this payment (null for a customer's
    # intended payment that is still pending).
    recorded_by_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("staff.id"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    paid_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    order: Mapped["Order"] = relationship(
        back_populates="payments",
    )

    recorder: Mapped["Staff | None"] = relationship()
