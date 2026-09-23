import uuid
from uuid import UUID

from sqlalchemy import Enum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base
from models.enums import TableStatusEnum


class Table(Base):
    __tablename__ = "tables"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    number: Mapped[int] = mapped_column(
        nullable=False,
        unique=True,
        index=True,
    )

    capacity: Mapped[int] = mapped_column(
        nullable=False,
    )

    status: Mapped[TableStatusEnum] = mapped_column(
        Enum(TableStatusEnum),
        default=TableStatusEnum.available,
        nullable=False,
    )

    orders: Mapped[list["Order"]] = relationship(
        back_populates="table",
    )
