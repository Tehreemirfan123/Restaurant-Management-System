from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_staff
from schemas.schemas import (
    InventoryItemCreate,
    InventoryItemResponse,
    InventoryItemUpdate,
)
from services.inventory_service import (
    create_inventory_item,
    delete_inventory_item,
    get_inventory_item,
    get_inventory_items,
    update_inventory_item,
)


router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
    dependencies=[Depends(get_current_staff)],
)


@router.get("", response_model=list[InventoryItemResponse])
def read_inventory(db: Session = Depends(get_db)):
    return get_inventory_items(db)


@router.get("/{item_id}", response_model=InventoryItemResponse)
def read_inventory_item(item_id: UUID, db: Session = Depends(get_db)):
    item = get_inventory_item(db, item_id)

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found",
        )

    return item


@router.post(
    "",
    response_model=InventoryItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_inventory_item(
    item_data: InventoryItemCreate,
    db: Session = Depends(get_db),
):
    return create_inventory_item(db, item_data)


@router.put("/{item_id}", response_model=InventoryItemResponse)
def edit_inventory_item(
    item_id: UUID,
    item_data: InventoryItemUpdate,
    db: Session = Depends(get_db),
):
    item = get_inventory_item(db, item_id)

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found",
        )

    return update_inventory_item(db, item, item_data)


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_inventory_item(item_id: UUID, db: Session = Depends(get_db)):
    item = get_inventory_item(db, item_id)

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found",
        )

    delete_inventory_item(db, item)
