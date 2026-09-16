from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from models.models import InventoryItem
from schemas.schemas import InventoryItemCreate, InventoryItemUpdate


def get_inventory_items(db: Session) -> list[InventoryItem]:
    return list(
        db.scalars(
            select(InventoryItem).order_by(InventoryItem.name)
        ).all()
    )


def get_inventory_item(
    db: Session,
    item_id: UUID,
) -> InventoryItem | None:
    return db.get(InventoryItem, item_id)


def create_inventory_item(
    db: Session,
    item_data: InventoryItemCreate,
) -> InventoryItem:
    existing = db.scalar(
        select(InventoryItem).where(
            InventoryItem.name == item_data.name
        )
    )

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Inventory item '{item_data.name}' already exists",
        )

    item = InventoryItem(**item_data.model_dump())

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


def update_inventory_item(
    db: Session,
    item: InventoryItem,
    item_data: InventoryItemUpdate,
) -> InventoryItem:
    updates = item_data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)

    return item


def delete_inventory_item(
    db: Session,
    item: InventoryItem,
) -> None:
    db.delete(item)
    db.commit()
