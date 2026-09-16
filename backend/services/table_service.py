from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from models.models import Table
from schemas.schemas import TableCreate, TableUpdate


def get_tables(db: Session) -> list[Table]:
    return list(
        db.scalars(
            select(Table).order_by(Table.number)
        ).all()
    )


def get_table(db: Session, table_id: UUID) -> Table | None:
    return db.get(Table, table_id)


def create_table(db: Session, table_data: TableCreate) -> Table:
    existing = db.scalar(
        select(Table).where(Table.number == table_data.number)
    )

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Table {table_data.number} already exists",
        )

    table = Table(**table_data.model_dump())

    db.add(table)
    db.commit()
    db.refresh(table)

    return table


def update_table(
    db: Session,
    table: Table,
    table_data: TableUpdate,
) -> Table:
    updates = table_data.model_dump(exclude_unset=True)

    new_number = updates.get("number")

    if new_number is not None and new_number != table.number:
        clash = db.scalar(
            select(Table).where(Table.number == new_number)
        )
        if clash is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Table {new_number} already exists",
            )

    for field, value in updates.items():
        setattr(table, field, value)

    db.commit()
    db.refresh(table)

    return table


def delete_table(db: Session, table: Table) -> None:
    db.delete(table)
    db.commit()
