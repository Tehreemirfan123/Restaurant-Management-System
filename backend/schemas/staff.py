from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from models.enums import RoleEnum


class StaffCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=100,
    )

    full_name: str = Field(
        min_length=1,
        max_length=150,
    )

    password: str = Field(
        min_length=6,
        max_length=128,
    )

    role: RoleEnum = RoleEnum.staff


class StaffResponse(BaseModel):
    id: UUID
    username: str
    full_name: str
    role: RoleEnum
    active: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: RoleEnum
    full_name: str
