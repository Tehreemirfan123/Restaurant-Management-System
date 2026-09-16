from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.schemas.schemas import (
    MenuItemCreate,
    MenuItemResponse,
    MenuItemUpdate,
)
from backend.services.menu_service import (
    create_menu_item,
    delete_menu_item,
    get_menu_item,
    get_menu_items,
    update_menu_item,
)


router = APIRouter(
    prefix="/menu",
    tags=["Menu"],
)


@router.get(
    "",
    response_model=list[MenuItemResponse],
)
def read_menu(
    db: Session = Depends(get_db),
):
    return get_menu_items(db)


@router.get(
    "/{menu_item_id}",
    response_model=MenuItemResponse,
)
def read_menu_item(
    menu_item_id: UUID,
    db: Session = Depends(get_db),
):
    menu_item = get_menu_item(
        db,
        menu_item_id,
    )

    if menu_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )

    return menu_item


@router.post(
    "",
    response_model=MenuItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_menu(
    menu_item_data: MenuItemCreate,
    db: Session = Depends(get_db),
):
    return create_menu_item(
        db,
        menu_item_data,
    )


@router.put(
    "/{menu_item_id}",
    response_model=MenuItemResponse,
)
def update_menu(
    menu_item_id: UUID,
    menu_item_data: MenuItemUpdate,
    db: Session = Depends(get_db),
):
    menu_item = get_menu_item(
        db,
        menu_item_id,
    )

    if menu_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )

    return update_menu_item(
        db,
        menu_item,
        menu_item_data,
    )


@router.delete(
    "/{menu_item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_menu(
    menu_item_id: UUID,
    db: Session = Depends(get_db),
):
    menu_item = get_menu_item(
        db,
        menu_item_id,
    )

    if menu_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )

    delete_menu_item(
        db,
        menu_item,
    )