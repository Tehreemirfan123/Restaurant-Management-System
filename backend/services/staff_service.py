from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.security import hash_password, verify_password
from backend.models.models import Staff
from backend.schemas.schemas import StaffCreate


def get_staff_by_username(
    db: Session,
    username: str,
) -> Staff | None:
    return db.scalar(
        select(Staff).where(
            Staff.username == username
        )
    )


def create_staff(
    db: Session,
    staff_data: StaffCreate,
) -> Staff:
    staff = Staff(
        username=staff_data.username,
        full_name=staff_data.full_name,
        hashed_password=hash_password(
            staff_data.password
        ),
        role=staff_data.role,
    )

    db.add(staff)
    db.commit()
    db.refresh(staff)

    return staff


def authenticate_staff(
    db: Session,
    username: str,
    password: str,
) -> Staff | None:
    staff = get_staff_by_username(db, username)

    if staff is None:
        return None

    if not staff.active:
        return None

    if not verify_password(
        password,
        staff.hashed_password,
    ):
        return None

    return staff


def list_staff(
    db: Session,
) -> list[Staff]:
    return list(
        db.scalars(
            select(Staff).order_by(Staff.username)
        ).all()
    )
