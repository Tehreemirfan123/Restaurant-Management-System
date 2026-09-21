from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_staff, require_admin
from schemas.schemas import (
    OrderingStatus,
    SettingsResponse,
    SettingsUpdate,
)
from services.settings_service import (
    get_settings,
    orders_today,
    update_settings,
)


router = APIRouter(
    prefix="/settings",
    tags=["Settings"],
)


@router.get(
    "/status",
    response_model=OrderingStatus,
)
def ordering_status(db: Session = Depends(get_db)):
    """Public: whether the kitchen is currently taking orders."""
    settings = get_settings(db)
    count = orders_today(db)
    accepting = settings.accepting_orders
    if settings.daily_order_cap is not None and count >= settings.daily_order_cap:
        accepting = False
    return {
        "accepting_orders": accepting,
        "orders_today": count,
        "daily_order_cap": settings.daily_order_cap,
        "delivery_fee": settings.delivery_fee,
        "restaurant_name": settings.restaurant_name,
        "contact_phone": settings.contact_phone,
        "address": settings.address,
        "opening_hours": settings.opening_hours,
        "delivery_radius_km": settings.delivery_radius_km,
    }


@router.get(
    "",
    response_model=SettingsResponse,
    dependencies=[Depends(get_current_staff)],
)
def read_settings(db: Session = Depends(get_db)):
    return get_settings(db)


@router.put(
    "",
    response_model=SettingsResponse,
    dependencies=[Depends(require_admin)],
)
def edit_settings(data: SettingsUpdate, db: Session = Depends(get_db)):
    return update_settings(db, data)
