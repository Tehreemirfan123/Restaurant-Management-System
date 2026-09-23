from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, object_session, selectinload

from models.models import (
    Customer,
    MenuItem,
    Order,
    OrderStatusEnum,
    OrderTypeEnum,
    OrderItem,
    Payment,
    PaymentStatusEnum,
    TableStatusEnum,
    Table,
)
from schemas.schemas import OrderCreate
from services.pricing import compute_advance
from services.settings_service import get_settings, orders_today


def create_order(
    db: Session,
    order_data: OrderCreate,
) -> Order:
    # Capacity gate: honour the accepting-orders switch and daily cap.
    settings = get_settings(db)
    if not settings.accepting_orders:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sorry, we are not accepting orders right now",
        )
    if (
        settings.daily_order_cap is not None
        and orders_today(db) >= settings.daily_order_cap
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="We've reached today's order limit. Please try tomorrow.",
        )

    menu_item_ids = [
        item.menu_item_id
        for item in order_data.items
    ]

    menu_items = db.scalars(
        select(MenuItem).where(
            MenuItem.id.in_(menu_item_ids)
        )
    ).all()

    menu_items_by_id = {
        menu_item.id: menu_item
        for menu_item in menu_items
    }

    if len(menu_items_by_id) != len(
        set(menu_item_ids)
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more menu items were not found",
        )

    # A dine-in order needs a table; validate any references that were given.
    if order_data.table_id is not None:
        table = db.get(Table, order_data.table_id)
        if table is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Table not found",
            )

    if (
        order_data.order_type == OrderTypeEnum.dine_in
        and order_data.table_id is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A dine-in order requires a table",
        )

    # A delivery order needs an address and carries the configured fee.
    delivery_fee = Decimal("0")
    delivery_distance = None
    if order_data.order_type == OrderTypeEnum.delivery:
        if not order_data.delivery_address:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A delivery order requires a delivery address",
            )
        # Changes in delivery charges in the code
        # Base fee covers up to delivery_radius_km; every extra km adds
        # delivery_per_km. All three values are configurable in Settings.
        delivery_fee = settings.delivery_fee
        delivery_distance = order_data.delivery_distance_km
        if (
            delivery_distance is not None
            and delivery_distance > settings.delivery_radius_km
        ):
            extra_km = delivery_distance - settings.delivery_radius_km
            delivery_fee += extra_km * settings.delivery_per_km

    # Resolve the customer: an explicit id, or find-or-create by phone so
    # repeat orders are tracked even for online checkouts.
    customer_id = order_data.customer_id

    if customer_id is not None:
        customer = db.get(Customer, customer_id)
        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found",
            )
    elif order_data.customer_phone:
        customer = db.scalar(
            select(Customer).where(
                Customer.phone == order_data.customer_phone
            )
        )
        if customer is None:
            customer = Customer(
                name=order_data.customer_name or "Customer",
                phone=order_data.customer_phone,
                address=order_data.delivery_address,
            )
            db.add(customer)
            db.flush()
        customer_id = customer.id

    order = Order(
        total_amount=0,
        order_type=order_data.order_type,
        category=order_data.category,
        delivery_fee=delivery_fee,
        delivery_address=order_data.delivery_address,
        delivery_distance_km=delivery_distance,
        table_id=order_data.table_id,
        customer_id=customer_id,
    )

    db.add(order)

    total_amount = 0

    for item_data in order_data.items:
        menu_item = menu_items_by_id[
            item_data.menu_item_id
        ]

        if not menu_item.available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"{menu_item.name} "
                    "is currently unavailable"
                ),
            )

        unit_price = menu_item.price

        subtotal = (
            unit_price * item_data.quantity
        )

        order_item = OrderItem(
            order=order,
            menu_item=menu_item,
            quantity=item_data.quantity,
            unit_price=unit_price,
        )

        db.add(order_item)

        total_amount += subtotal

    order.total_amount = total_amount + delivery_fee

    # If the customer picked an intended payment method, record a pending
    # payment so it surfaces in reconciliation until staff confirm receipt.
    # Advance-required orders record the advance amount; others the full total.
    if order_data.payment_method is not None:
        advance_required, advance_amount = compute_advance(
            order.total_amount, order.category, settings
        )
        intended = (
            advance_amount
            if advance_required and advance_amount > 0
            else order.total_amount
        )
        db.add(
            Payment(
                order=order,
                amount=intended,
                method=order_data.payment_method,
                status=PaymentStatusEnum.pending,
            )
        )

    db.commit()
    db.refresh(order)

    return _annotate(order)


def _annotate(order: Order, settings=None) -> Order:
    """Attach transient customer/payment roll-up fields for the API response.

    Pass ``settings`` when annotating many orders in a loop so we don't query
    the settings row once per order.
    """
    order.customer_name = order.customer.name if order.customer else None

    paid = sum(
        (p.amount for p in order.payments if p.status == PaymentStatusEnum.paid),
        Decimal("0"),
    )
    has_refund = any(
        p.status == PaymentStatusEnum.refunded for p in order.payments
    )
    total = order.total_amount or Decimal("0")

    order.amount_paid = paid
    order.balance_due = max(total - paid, Decimal("0"))

    if paid <= 0:
        order.payment_status = "refunded" if has_refund else "unpaid"
    elif paid >= total:
        order.payment_status = "paid"
    else:
        order.payment_status = "partial"

    if settings is None:
        session = object_session(order)
        settings = get_settings(session) if session is not None else None

    if settings is not None:
        required, amount = compute_advance(total, order.category, settings)
        order.advance_required = required
        order.advance_amount = amount
    else:
        order.advance_required = False
        order.advance_amount = Decimal("0")

    return order


def get_orders(
    db: Session,
    limit: int = 500,
    offset: int = 0,
) -> list[Order]:
    # Fetch settings once, and eager-load relationships to avoid N+1 queries.
    settings = get_settings(db)
    orders = db.scalars(
        select(Order)
        .options(
            selectinload(Order.items),
            selectinload(Order.customer),
            selectinload(Order.payments),
        )
        .order_by(Order.created_at.desc())
        .offset(offset)
        .limit(limit)
    ).all()
    return [_annotate(o, settings) for o in orders]


def get_order(
    db: Session,
    order_id: UUID,
) -> Order | None:
    order = db.get(Order, order_id)
    return _annotate(order) if order is not None else None


def update_order_status(
    db: Session,
    order: Order,
    status_value,
) -> Order:
    order.status = status_value

    db.commit()
    db.refresh(order)

    return _annotate(order)


def cancel_order(
    db: Session,
    order: Order,
) -> Order:
    """Cancel an order, refund a paid payment, and free its table."""
    if order.status == OrderStatusEnum.cancelled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order is already cancelled",
        )

    order.status = OrderStatusEnum.cancelled

    # Refund any settled payments; drop still-pending intents.
    for payment in order.payments:
        if payment.status == PaymentStatusEnum.paid:
            payment.status = PaymentStatusEnum.refunded

    if order.table is not None:
        order.table.status = TableStatusEnum.available

    db.commit()
    db.refresh(order)

    return _annotate(order)