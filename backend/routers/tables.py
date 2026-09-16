from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_staff
from schemas.schemas import (
    TableCreate,
    TableResponse,
    TableUpdate,
)
from services.table_service import (
    create_table,
    delete_table,
    get_table,
    get_tables,
    update_table,
)


router = APIRouter(
    prefix="/tables",
    tags=["Tables"],
    dependencies=[Depends(get_current_staff)],
)


@router.get("", response_model=list[TableResponse])
def read_tables(db: Session = Depends(get_db)):
    return get_tables(db)


@router.get("/{table_id}", response_model=TableResponse)
def read_table(table_id: UUID, db: Session = Depends(get_db)):
    table = get_table(db, table_id)

    if table is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Table not found",
        )

    return table


@router.post(
    "",
    response_model=TableResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_table(table_data: TableCreate, db: Session = Depends(get_db)):
    return create_table(db, table_data)


@router.put("/{table_id}", response_model=TableResponse)
def edit_table(
    table_id: UUID,
    table_data: TableUpdate,
    db: Session = Depends(get_db),
):
    table = get_table(db, table_id)

    if table is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Table not found",
        )

    return update_table(db, table, table_data)


@router.delete(
    "/{table_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_table(table_id: UUID, db: Session = Depends(get_db)):
    table = get_table(db, table_id)

    if table is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Table not found",
        )

    delete_table(db, table)
