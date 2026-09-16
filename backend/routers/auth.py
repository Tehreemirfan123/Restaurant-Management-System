from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from core.security import create_access_token
from database.database import get_db
from dependencies.auth import get_current_staff, require_admin
from models.models import Staff
from schemas.schemas import (
    StaffCreate,
    StaffResponse,
    Token,
)
from services.staff_service import (
    authenticate_staff,
    create_staff,
    get_staff_by_username,
    list_staff,
)


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post(
    "/login",
    response_model=Token,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    staff = authenticate_staff(
        db,
        form_data.username,
        form_data.password,
    )

    if staff is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        subject=staff.username,
        role=staff.role.value,
    )

    return Token(
        access_token=access_token,
        role=staff.role,
        full_name=staff.full_name,
    )


@router.get(
    "/me",
    response_model=StaffResponse,
)
def read_current_staff(
    current_staff: Staff = Depends(get_current_staff),
):
    return current_staff


@router.get(
    "/staff",
    response_model=list[StaffResponse],
)
def read_staff(
    db: Session = Depends(get_db),
    _: Staff = Depends(require_admin),
):
    return list_staff(db)


@router.post(
    "/staff",
    response_model=StaffResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_staff(
    staff_data: StaffCreate,
    db: Session = Depends(get_db),
    _: Staff = Depends(require_admin),
):
    existing = get_staff_by_username(
        db,
        staff_data.username,
    )

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    return create_staff(db, staff_data)
