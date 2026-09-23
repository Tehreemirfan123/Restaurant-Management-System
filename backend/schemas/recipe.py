from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RecipeIngredientCreate(BaseModel):
    inventory_item_id: UUID
    quantity: Decimal = Field(gt=0, decimal_places=3)


class RecipeCreate(BaseModel):
    menu_item_id: UUID
    notes: str | None = None
    ingredients: list[RecipeIngredientCreate] = Field(default_factory=list)


class RecipeUpdate(BaseModel):
    notes: str | None = None
    ingredients: list[RecipeIngredientCreate] | None = None


class RecipeIngredientResponse(BaseModel):
    id: UUID
    inventory_item_id: UUID
    quantity: Decimal

    model_config = ConfigDict(from_attributes=True)


class RecipeResponse(BaseModel):
    id: UUID
    menu_item_id: UUID
    notes: str | None
    ingredients: list[RecipeIngredientResponse]

    model_config = ConfigDict(from_attributes=True)
