from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.models import MenuItem
from backend.schemas.schemas import (
    MenuItemCreate,
    MenuItemUpdate,
)


def get_menu_items(
    db: Session,
) -> list[MenuItem]:
    return list(
        db.scalars(
            select(MenuItem)
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