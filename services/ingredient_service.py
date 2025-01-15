from models.models_sql import RecipeIngredient, Ingredient
from extensions import db


def validate_ingredient_data(name_ingredient, quantity, unit):
    errors = {}
    if not name_ingredient or len(name_ingredient) < 2:
        errors["name_ingredient"] = (
            "Le nom de l'ingrédient doit comporter au moins 2 caractères."
        )
    if not isinstance(quantity, (int, float)) or quantity <= 0:
        errors["quantity"] = "La quantité doit être un nombre positif."
    if not unit or len(unit) < 1:
        errors["unit"] = "L'unité est requise."
    return errors


def add_ingredient_to_recipe(recipe_id, name_ingredient, quantity, unit):
    try:
        # Valider les données
        errors = validate_ingredient_data(name_ingredient, quantity, unit)
        if errors:
            return {"error": True, "message": errors}

        # Vérification ou ajout de l'ingrédient
        ingredient = Ingredient.query.filter_by(name_ingredient=name_ingredient).first()
        if not ingredient:
            ingredient = Ingredient(name_ingredient=name_ingredient)
            db.session.add(ingredient)
            db.session.flush()

        # Vérifier si la relation existe déjà
        existing = RecipeIngredient.query.filter_by(
            recipe_id=recipe_id, ingredient_id=ingredient.id
        ).first()
        if existing:
            existing.quantity = float(quantity)
            existing.unit = unit
        else:
            new_relation = RecipeIngredient(
                recipe_id=recipe_id,
                ingredient_id=ingredient.id,
                quantity=float(quantity),
                unit=unit,
            )
            db.session.add(new_relation)

        db.session.commit()
        return {"error": False, "message": "Ingredient added successfully."}

    except Exception as e:
        db.session.rollback()
        return {"error": True, "message": str(e)}


def delete_ingredient(recipe_id, ingredient_id):
    try:
        recipe_ingredient = RecipeIngredient.query.filter_by(
            recipe_id=recipe_id, ingredient_id=ingredient_id
        ).first_or_404()
        db.session.delete(recipe_ingredient)
        db.session.commit()
        return {"error": False, "message": "Ingredient removed from recipe."}

    except Exception as e:
        return {"error": True, "message": str(e)}


def update_ingredient(recipe_id, ingredient_id, quantity, unit):
    try:
        recipe_ingredient = RecipeIngredient.query.filter_by(
            recipe_id=recipe_id, ingredient_id=ingredient_id
        ).first()

        if recipe_ingredient:
            if quantity:
                recipe_ingredient.quantity = quantity
            if unit:
                recipe_ingredient.unit = unit
            db.session.commit()
            return {"error": False, "message": "Ingredient updated successfully."}
        else:
            return {"error": True, "message": "Ingredient not found."}

    except Exception as e:
        return {"error": True, "message": str(e)}
