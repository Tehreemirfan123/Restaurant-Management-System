from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_staff
from schemas.schemas import (
    RecipeCreate,
    RecipeResponse,
    RecipeUpdate,
)
from services.recipe_service import (
    create_recipe,
    delete_recipe,
    get_recipe,
    get_recipes,
    update_recipe,
)


router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"],
    dependencies=[Depends(get_current_staff)],
)


@router.get("", response_model=list[RecipeResponse])
def read_recipes(db: Session = Depends(get_db)):
    return get_recipes(db)


@router.get("/{recipe_id}", response_model=RecipeResponse)
def read_recipe(recipe_id: UUID, db: Session = Depends(get_db)):
    recipe = get_recipe(db, recipe_id)

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    return recipe


@router.post(
    "",
    response_model=RecipeResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_recipe(recipe_data: RecipeCreate, db: Session = Depends(get_db)):
    return create_recipe(db, recipe_data)


@router.put("/{recipe_id}", response_model=RecipeResponse)
def edit_recipe(
    recipe_id: UUID,
    recipe_data: RecipeUpdate,
    db: Session = Depends(get_db),
):
    recipe = get_recipe(db, recipe_id)

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    return update_recipe(db, recipe, recipe_data)


@router.delete(
    "/{recipe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_recipe(recipe_id: UUID, db: Session = Depends(get_db)):
    recipe = get_recipe(db, recipe_id)

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    delete_recipe(db, recipe)
