from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FeedbackCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    would_reorder: bool = True
    comment: str | None = None


class FeedbackResponse(BaseModel):
    id: UUID
    order_id: UUID
    rating: int
    would_reorder: bool
    comment: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
