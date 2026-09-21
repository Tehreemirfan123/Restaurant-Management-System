from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.config import local_today
from models.models import DayOfWeekEnum, MenuItem
from schemas.schemas import (
    MenuItemCreate,
    MenuItemUpdate,
)

# Python's weekday() (Mon=0 .. Sun=6) mapped to our enum.
_WEEKDAYS = [
    DayOfWeekEnum.monday,
    DayOfWeekEnum.tuesday,
    DayOfWeekEnum.wednesday,
    DayOfWeekEnum.thursday,
    DayOfWeekEnum.friday,
    DayOfWeekEnum.saturday,
    DayOfWeekEnum.sunday,
]


def get_menu_items(
    db: Session,
) -> list[MenuItem]:
    return list(
        db.scalars(
            select(MenuItem)
            .order_by(MenuItem.name)
        ).all()
    )


def get_todays_menu(
    db: Session,
) -> list[MenuItem]:
    """Available dishes for today: the day's rotating dish plus any
    day-agnostic items (specials with no set day)."""
    today = _WEEKDAYS[local_today().weekday()]

    return list(
        db.scalars(
            select(MenuItem)
            .where(
                MenuItem.available.is_(True),
                (MenuItem.day_of_week == today)
                | (MenuItem.day_of_week.is_(None)),
            )
            .order_by(MenuItem.name)
        ).all()
    )


def get_menu_item(
    db: Session,
    menu_item_id: UUID,
) -> MenuItem | None:
    return db.get(
        MenuItem,
        menu_item_id,
    )


def create_menu_item(
    db: Session,
    menu_item_data: MenuItemCreate,
) -> MenuItem:
    menu_item = MenuItem(
        **menu_item_data.model_dump()
    )

    db.add(menu_item)
    db.commit()
    db.refresh(menu_item)

    return menu_item


def update_menu_item(
    db: Session,
    menu_item: MenuItem,
    menu_item_data: MenuItemUpdate,
) -> MenuItem:
    updates = menu_item_data.model_dump(
        exclude_unset=True
    )

    for field, value in updates.items():
        setattr(
            menu_item,
            field,
            value,
        )

    db.commit()
    db.refresh(menu_item)

    return menu_item


def delete_menu_item(
    db: Session,
    menu_item: MenuItem,
) -> None:
    db.delete(menu_item)
    db.commit()