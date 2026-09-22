import enum
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
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base


class CategoryEnum(str, enum.Enum):
    starters = "starters"
    mains = "mains"
    desserts = "desserts"
    drinks = "drinks"


class OrderStatusEnum(str, enum.Enum):
    received = "received"
    preparing = "preparing"
    ready = "ready"
    delivered = "delivered"
    cancelled = "cancelled"

class PaymentMethodEnum(str, enum.Enum):
    cash = "cash"
    card = "card"
    bank_transfer = "bank_transfer"
    online = "online"
    jazzcash = "jazzcash"
    easypaisa = "easypaisa"


class PaymentStatusEnum(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"
    refunded = "refunded"


class RoleEnum(str, enum.Enum):
    admin = "admin"
    staff = "staff"


class TableStatusEnum(str, enum.Enum):
    available = "available"
    occupied = "occupied"
    reserved = "reserved"


class OrderTypeEnum(str, enum.Enum):
    # pickup/delivery are the live fulfilment types for the home kitchen.
    # dine_in/takeaway are kept for backwards compatibility but hidden in the UI.
    pickup = "pickup"
    delivery = "delivery"
    dine_in = "dine_in"
    takeaway = "takeaway"


class OrderCategoryEnum(str, enum.Enum):
    # Regular orders may pay cash on delivery. Custom / subscription orders
    # (and any order over the large-order threshold) require an advance.
    regular = "regular"
    custom = "custom"
    subscription = "subscription"
    large = "large"


class DayOfWeekEnum(str, enum.Enum):
    monday = "monday"
    tuesday = "tuesday"
    wednesday = "wednesday"
    thursday = "thursday"
    friday = "friday"
    saturday = "saturday"
    sunday = "sunday"


class CustomerSegmentEnum(str, enum.Enum):
    office = "office"
    student = "student"
    hostel = "hostel"
    household = "household"
    other = "other"


class Staff(Base):
    __tablename__ = "staff"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    username: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[RoleEnum] = mapped_column(
        Enum(RoleEnum),
        default=RoleEnum.staff,
        nullable=False,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


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


class Order(Base):
    __tablename__ = "orders"

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
        unique=True,
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

class Payment(Base):
    __tablename__ = "payments"

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
        unique=True,
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

class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    phone: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
        index=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    address: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    segment: Mapped[CustomerSegmentEnum | None] = mapped_column(
        Enum(CustomerSegmentEnum),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    orders: Mapped[list["Order"]] = relationship(
        back_populates="customer",
    )


class Table(Base):
    __tablename__ = "tables"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    number: Mapped[int] = mapped_column(
        nullable=False,
        unique=True,
        index=True,
    )

    capacity: Mapped[int] = mapped_column(
        nullable=False,
    )

    status: Mapped[TableStatusEnum] = mapped_column(
        Enum(TableStatusEnum),
        default=TableStatusEnum.available,
        nullable=False,
    )

    orders: Mapped[list["Order"]] = relationship(
        back_populates="table",
    )


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
