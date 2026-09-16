import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.core.security import decode_access_token
from backend.database.database import get_db
from backend.models.models import RoleEnum, Staff
from backend.services.staff_service import get_staff_by_username


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


_credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_staff(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Staff:
    try:
        payload = decode_access_token(token)
        username = payload.get("sub")

        if username is None:
            raise _credentials_exception

    except jwt.PyJWTError:
        raise _credentials_exception

    staff = get_staff_by_username(db, username)

    if staff is None or not staff.active:
        raise _credentials_exception

    return staff


def require_admin(
    current_staff: Staff = Depends(get_current_staff),
) -> Staff:
    if current_staff.role != RoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )

    return current_staff
