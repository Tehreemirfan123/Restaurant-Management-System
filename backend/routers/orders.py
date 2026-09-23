from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from core.rate_limit import limiter
from database.database import get_db
from dependencies.auth import get_current_staff
from models.models import OrderFeedback
from schemas.schemas import (
    FeedbackCreate,
    FeedbackResponse,
    OrderCreate,
    OrderResponse,
    OrderStatusUpdate,
)
from services.order_service import (
    cancel_order,
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
@limiter.limit("20/minute")
def create_new_order(
    request: Request,
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
    _: object = Depends(get_current_staff),
    limit: int = Query(default=500, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
):
    # Staff-only: the full list exposes customer names, phones and addresses.
    return get_orders(db, limit=limit, offset=offset)


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
    _: object = Depends(get_current_staff),
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


@router.post(
    "/{order_id}/cancel",
    response_model=OrderResponse,
)
def cancel(
    order_id: UUID,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_staff),
):
    order = get_order(db, order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    return cancel_order(db, order)


@router.get(
    "/{order_id}/feedback",
    response_model=FeedbackResponse,
)
def read_feedback(order_id: UUID, db: Session = Depends(get_db)):
    order = get_order(db, order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    if order.feedback is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No feedback yet",
        )
    return order.feedback


@router.post(
    "/{order_id}/feedback",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("20/minute")
def submit_feedback(
    request: Request,
    order_id: UUID,
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db),
):
    order = get_order(db, order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    if order.feedback is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Feedback already submitted for this order",
        )

    feedback = OrderFeedback(
        order_id=order.id,
        rating=feedback_data.rating,
        would_reorder=feedback_data.would_reorder,
        comment=feedback_data.comment,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback