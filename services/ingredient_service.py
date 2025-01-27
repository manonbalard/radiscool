from models.models_sql import RecipeIngredient, Ingredient
from extensions import db


def validate_ingredient_data(name_ingredient, quantity, unit):
    """
    Validate the data for an ingredient.

    Args:
        name_ingredient (str): The name of the ingredient.
        quantity (int | float): The quantity of the ingredient.
        unit (str): The unit of measurement for the ingredient.

    Returns:
        dict: A dictionary containing validation errors, if any.
    """
    errors = {}

    # Ensure the ingredient name is at least 2 characters long.
    if not name_ingredient or len(name_ingredient) < 2:
        errors["name_ingredient"] = (
            "The ingredient name must be at least 2 characters long."
        )

    # Validate that the quantity is a positive number (including float).
    if not isinstance(quantity, (int, float)) or quantity <= 0:
        errors["quantity"] = "The quantity must be a positive number."

    # Unit is optional, so we only check it if it is provided.
    if unit and len(unit) < 1:
        errors["unit"] = "The unit cannot be empty if provided."

    return errors


def add_ingredient_to_recipe(recipe_id, name_ingredient, quantity, unit):
    """
    Add an ingredient to a recipe or update its quantity and unit if it already exists.

    Args:
        recipe_id (int): The ID of the recipe.
        name_ingredient (str): The name of the ingredient.
        quantity (float): The quantity of the ingredient.
        unit (str): The unit of measurement for the ingredient.

    Returns:
        dict: A dictionary indicating success or error, with a message.
    """
    try:
        # Valider les données de l'ingrédient.
        errors = validate_ingredient_data(name_ingredient, quantity, unit)
        if errors:
            return {"error": True, "message": errors}

        # Vérifier si l'ingrédient existe déjà dans la base de données.
        ingredient = Ingredient.query.filter_by(name_ingredient=name_ingredient).first()

        # Si l'ingrédient n'existe pas, on l'ajoute à la base de données.
        if not ingredient:
            ingredient = Ingredient(name_ingredient=name_ingredient)
            db.session.add(ingredient)
            db.session.flush()  # Assure que l'ID de l'ingrédient est disponible

        # Récupérer l'ID de l'ingrédient (pour l'envoyer dans la réponse)
        ingredient_id = ingredient.id

        # Vérifier si l'ingrédient est déjà associé à la recette
        existing = RecipeIngredient.query.filter_by(
            recipe_id=recipe_id, ingredient_id=ingredient_id
        ).first()

        if existing:
            # Si l'ingrédient existe déjà pour cette recette, on met à jour la quantité et l'unité
            existing.quantity = float(quantity)
            existing.unit = unit
        else:
            # Ajouter la nouvelle relation entre la recette et l'ingrédient
            new_relation = RecipeIngredient(
                recipe_id=recipe_id,
                ingredient_id=ingredient_id,
                quantity=float(quantity),
                unit=unit,
            )
            db.session.add(new_relation)

        # Valider les changements dans la base de données
        db.session.commit()

        return {
            "error": False,
            "message": "Ingredient added successfully.",
            "ingredient_id": ingredient_id,
        }

    except Exception as e:
        db.session.rollback()
        return {"error": True, "message": str(e)}


def delete_ingredient(recipe_id, ingredient_id):
    """
    Remove an ingredient from a recipe.

    Args:
        recipe_id (int): The ID of the recipe.
        ingredient_id (int): The ID of the ingredient.

    Returns:
        dict: A dictionary indicating success or error, with a message.
    """
    try:
        # Locate the recipe-ingredient relationship.
        recipe_ingredient = RecipeIngredient.query.filter_by(
            recipe_id=recipe_id, ingredient_id=ingredient_id
        ).first_or_404()

        # Delete the relationship from the database.
        db.session.delete(recipe_ingredient)
        db.session.commit()
        return {"error": False, "message": "Ingredient removed from recipe."}

    except Exception as e:
        # Handle any exceptions that occur during deletion.
        return {"error": True, "message": str(e)}


def update_ingredient(recipe_id, ingredient_id, quantity, unit):
    """
    Update the quantity and/or unit of an ingredient in a recipe.

    Args:
        recipe_id (int): The ID of the recipe.
        ingredient_id (int): The ID of the ingredient.
        quantity (float): The new quantity of the ingredient (optional).
        unit (str): The new unit of measurement for the ingredient (optional).

    Returns:
        dict: A dictionary indicating success or error, with a message.
    """
    try:
        # Locate the recipe-ingredient relationship.
        recipe_ingredient = RecipeIngredient.query.filter_by(
            recipe_id=recipe_id, ingredient_id=ingredient_id
        ).first()

        if recipe_ingredient:
            # Update the quantity if provided.
            if quantity:
                recipe_ingredient.quantity = quantity

            # Update the unit if provided.
            if unit:
                recipe_ingredient.unit = unit

            # Commit the changes to the database.
            db.session.commit()
            return {"error": False, "message": "Ingredient updated successfully."}
        else:
            # Handle cases where the ingredient is not found in the recipe.
            return {"error": True, "message": "Ingredient not found."}

    except Exception as e:
        # Handle any exceptions that occur during the update process.
        return {"error": True, "message": str(e)}
