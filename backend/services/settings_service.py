from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models.models import Order, Settings
from schemas.schemas import SettingsUpdate


def get_settings(db: Session) -> Settings:
    """Return the single settings row, creating it with defaults if missing."""
    settings = db.scalar(select(Settings))
    if settings is None:
        settings = Settings(accepting_orders=True, daily_order_cap=None)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


def update_settings(db: Session, data: SettingsUpdate) -> Settings:
    settings = get_settings(db)
    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(settings, field, value)
    db.commit()
    db.refresh(settings)
    return settings


def orders_today(db: Session) -> int:
    today = datetime.now(timezone.utc).date()
    return db.scalar(
        select(func.count(Order.id)).where(
            func.date(Order.created_at) == today
        )
    ) or 0
