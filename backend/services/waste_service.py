from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from models.models import InventoryItem, WasteLog
from schemas.schemas import WasteLogCreate


def _to_dict(log: WasteLog) -> dict:
    item = log.inventory_item
    cost = Decimal("0")
    if item is not None:
        cost = (log.quantity or Decimal("0")) * (item.unit_cost or Decimal("0"))
    return {
        "id": log.id,
        "inventory_item_id": log.inventory_item_id,
        "item_name": item.name if item is not None else None,
        "description": log.description,
        "quantity": log.quantity,
        "cost": cost,
        "created_at": log.created_at,
    }


def list_waste(db: Session) -> list[dict]:
    logs = db.scalars(
        select(WasteLog).order_by(WasteLog.created_at.desc())
    ).all()
    return [_to_dict(log) for log in logs]


def create_waste(db: Session, data: WasteLogCreate) -> dict:
    if data.inventory_item_id is not None:
        item = db.get(InventoryItem, data.inventory_item_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventory item not found",
            )

    log = WasteLog(
        inventory_item_id=data.inventory_item_id,
        description=data.description,
        quantity=data.quantity,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return _to_dict(log)


def total_waste_value(db: Session) -> Decimal:
    logs = db.scalars(select(WasteLog)).all()
    total = Decimal("0")
    for log in logs:
        item = log.inventory_item
        if item is not None:
            total += (log.quantity or Decimal("0")) * (
                item.unit_cost or Decimal("0")
            )
    return total
