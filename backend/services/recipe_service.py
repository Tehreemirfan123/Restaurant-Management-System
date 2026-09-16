from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from models.models import (
    InventoryItem,
    MenuItem,
    Recipe,
    RecipeIngredient,
)
from schemas.schemas import (
    RecipeCreate,
    RecipeIngredientCreate,
    RecipeUpdate,
)


def _validate_ingredients(
    db: Session,
    ingredients: list[RecipeIngredientCreate],
) -> None:
    inventory_ids = [ing.inventory_item_id for ing in ingredients]

    if not inventory_ids:
        return

    found = db.scalars(
        select(InventoryItem.id).where(
            InventoryItem.id.in_(inventory_ids)
        )
    ).all()

    if len(set(found)) != len(set(inventory_ids)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more inventory items were not found",
        )


def get_recipes(db: Session) -> list[Recipe]:
    return list(db.scalars(select(Recipe)).all())


def get_recipe(db: Session, recipe_id: UUID) -> Recipe | None:
    return db.get(Recipe, recipe_id)


def get_recipe_for_menu_item(
    db: Session,
    menu_item_id: UUID,
) -> Recipe | None:
    return db.scalar(
        select(Recipe).where(Recipe.menu_item_id == menu_item_id)
    )


def create_recipe(db: Session, recipe_data: RecipeCreate) -> Recipe:
    menu_item = db.get(MenuItem, recipe_data.menu_item_id)

    if menu_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )

    if get_recipe_for_menu_item(db, recipe_data.menu_item_id) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This menu item already has a recipe",
        )

    _validate_ingredients(db, recipe_data.ingredients)

    recipe = Recipe(
        menu_item_id=recipe_data.menu_item_id,
        notes=recipe_data.notes,
    )

    for ing in recipe_data.ingredients:
        recipe.ingredients.append(
            RecipeIngredient(
                inventory_item_id=ing.inventory_item_id,
                quantity=ing.quantity,
            )
        )

    db.add(recipe)
    db.commit()
    db.refresh(recipe)

    return recipe


def update_recipe(
    db: Session,
    recipe: Recipe,
    recipe_data: RecipeUpdate,
) -> Recipe:
    if recipe_data.notes is not None:
        recipe.notes = recipe_data.notes

    # When an ingredient list is supplied, replace the recipe's
    # ingredients wholesale.
    if recipe_data.ingredients is not None:
        _validate_ingredients(db, recipe_data.ingredients)

        recipe.ingredients.clear()

        for ing in recipe_data.ingredients:
            recipe.ingredients.append(
                RecipeIngredient(
                    inventory_item_id=ing.inventory_item_id,
                    quantity=ing.quantity,
                )
            )

    db.commit()
    db.refresh(recipe)

    return recipe


def delete_recipe(db: Session, recipe: Recipe) -> None:
    db.delete(recipe)
    db.commit()
