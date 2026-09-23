from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from models.enums import TableStatusEnum


class TableCreate(BaseModel):
    number: int = Field(gt=0)
    capacity: int = Field(gt=0)
    status: TableStatusEnum = TableStatusEnum.available


class TableUpdate(BaseModel):
    number: int | None = Field(default=None, gt=0)
    capacity: int | None = Field(default=None, gt=0)
    status: TableStatusEnum | None = None


class TableResponse(BaseModel):
    id: UUID
    number: int
    capacity: int
    status: TableStatusEnum

    model_config = ConfigDict(from_attributes=True)
