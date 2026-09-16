from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.database import get_db
from schemas.schemas import (
    OrderCreate,
    OrderResponse,
    OrderStatusUpdate,
)
from services.order_service import (
    create_order,
    get_order,
    get_orders,
    update_order_status,
)


router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
):
    return create_order(
        db,
        order_data,
    )


@router.get(
    "",
    response_model=list[OrderResponse],
)
def read_orders(
    db: Session = Depends(get_db),
):
    return get_orders(db)


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
)
def read_order(
    order_id: UUID,
    db: Session = Depends(get_db),
):
    order = get_order(
        db,
        order_id,
    )

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    return order


@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
)
def change_order_status(
    order_id: UUID,
    status_data: OrderStatusUpdate,
    db: Session = Depends(get_db),
):
    order = get_order(
        db,
        order_id,
    )

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    return update_order_status(
        db,
        order,
        status_data.status,
    )