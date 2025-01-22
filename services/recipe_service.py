from flask import current_app
from models.models_sql import Recipe, RecipeIngredient, Ingredient, Rating
from extensions import db
import json
import imghdr
import os
import re


def secure_filename(filename):
    """
    Securely sanitizes a given filename by removing unwanted characters
    and ensuring it does not contain potentially dangerous extensions.

    This function replaces any non-alphanumeric characters (except for hyphens,
    underscores, and periods) with underscores, and ensures the returned filename
    is safe to use in file systems.

    Args:
        filename (str): The original filename to be sanitized.

    Returns:
        str: The sanitized and secure filename.
    """
    # Replace non-alphanumeric characters (except hyphens, underscores, and periods)
    # with underscores.
    filename = re.sub(r"[^a-zA-Z0-9_.-]", "_", filename)

    # Return the basename of the filename to avoid directory traversal risks
    # and to extract the filename without any path.
    return os.path.basename(filename)


def allowed_file(filename):
    """
    Check if a file has an allowed extension.

    Args:
        filename (str): The name of the file.

    Returns:
        bool: True if the file has an allowed extension, False otherwise.
    """
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


def validate_image(file):
    """
    Validate whether the provided file is a valid image.

    Args:
        file (FileStorage): The file to validate.

    Returns:
        bool: True if the file is a valid image, False otherwise.
    """
    if not file:
        return False
    file_type = imghdr.what(file)
    return file_type in current_app.config["ALLOWED_EXTENSIONS"]


def validate_recipe_data(title, description, ingredients_json):
    """
    Validate the data for creating or editing a recipe.

    Args:
        title (str): The title of the recipe.
        description (str): The description of the recipe.
        ingredients_json (str): JSON string of the ingredients.

    Returns:
        dict: A dictionary containing validation errors, if any.
    """
    errors = {}
    if not title or len(title) < 3:
        errors["title"] = "The title must be at least 3 characters long."
    if not isinstance(ingredients_json, str):
        errors["ingredients_json"] = "Ingredients must be a valid JSON string."
    return errors


def add_recipe(title, description, ingredients_json, user_id, image_file):
    """
    Add a new recipe to the database.

    Args:
        title (str): The title of the recipe.
        description (str): The description of the recipe.
        ingredients_json (str): JSON string of the ingredients.
        user_id (int): The ID of the user creating the recipe.
        image_file (FileStorage): An optional image file for the recipe.

    Returns:
        dict: Result indicating success or failure, with a message.
    """
    try:
        # Validate recipe data.
        errors = validate_recipe_data(title, description, ingredients_json)
        if errors:
            return {"error": True, "message": errors}

        # Load ingredients from JSON.
        ingredients = json.loads(ingredients_json)
        new_recipe = Recipe(title=title, description=description, user_id=user_id)

        # Handle image upload.
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            upload_folder = current_app.config["UPLOADED_PHOTOS_DEST"]
            file_path = os.path.join(upload_folder, filename)
            image_file.save(file_path)
            new_recipe.image = "uploads/images/" + filename

        db.session.add(new_recipe)
        db.session.flush()  # Make the recipe ID available.

        # Add ingredients and their relationships.
        for ingredient_data in ingredients:
            ingredient_name = ingredient_data["name"]
            ingredient = Ingredient.query.filter_by(
                name_ingredient=ingredient_name
            ).first()
            if not ingredient:
                ingredient = Ingredient(name_ingredient=ingredient_name)
                db.session.add(ingredient)
                db.session.flush()

            new_recipe_ingredient = RecipeIngredient(
                recipe_id=new_recipe.id,
                ingredient_id=ingredient.id,
                quantity=ingredient_data["quantity"],
                unit=ingredient_data["unit"],
            )
            db.session.add(new_recipe_ingredient)

        db.session.commit()
        return {"error": False, "recipe_id": new_recipe.id}

    except Exception as e:
        db.session.rollback()
        return {"error": True, "message": str(e)}


def get_recipe_with_comments(id):
    """
    Retrieve a recipe along with its comments.

    Args:
        id (int): The ID of the recipe.

    Returns:
        dict: A dictionary containing the recipe and its comments.
    """
    try:
        recipe = Recipe.query.get_or_404(id)
        comments = recipe.get_comments()
        return {"error": False, "recipe": recipe, "comments": comments}

    except Exception as e:
        return {"error": True, "message": str(e)}


def validate_id(id_value, id_name="ID"):
    """
    Validate if a provided ID is a positive integer.

    Args:
        id_value (int): The ID value to validate.
        id_name (str): The name of the ID for error messages.

    Returns:
        str | None: Error message if validation fails, otherwise None.
    """
    if not isinstance(id_value, int) or id_value <= 0:
        return f"{id_name} must be a positive integer."
    return None


def delete_recipe(id):
    """
    Delete a recipe and its unused ingredients.

    Args:
        id (int): The ID of the recipe to delete.

    Returns:
        dict: Result indicating success or failure, with a message.
    """
    try:
        error = validate_id(id, "Recipe ID")
        if error:
            return {"error": True, "message": error}

        # Retrieve the recipe to delete.
        recipe = Recipe.query.get_or_404(id)

        # Retrieve ingredients related to the recipe.
        recipe_ingredients = RecipeIngredient.query.filter_by(recipe_id=recipe.id).all()

        # Delete RecipeIngredient relationships.
        RecipeIngredient.query.filter_by(recipe_id=recipe.id).delete()

        # Check and delete unused ingredients.
        for relation in recipe_ingredients:
            ingredient_id = relation.ingredient_id
            other_relations = RecipeIngredient.query.filter_by(
                ingredient_id=ingredient_id
            ).count()
            if other_relations == 0:
                Ingredient.query.filter_by(id=ingredient_id).delete()

        # Delete the recipe.
        db.session.delete(recipe)
        db.session.commit()

        return {"error": False, "message": "Recipe and unused ingredients deleted."}

    except Exception as e:
        db.session.rollback()
        return {"error": True, "message": str(e)}


def edit_recipe(id, title, description, ingredients_json, image_file=None):
    """
    Edit an existing recipe.

    Args:
        id (int): The ID of the recipe to edit.
        title (str): The updated title of the recipe.
        description (str): The updated description of the recipe.
        ingredients_json (str): JSON string of the updated ingredients.
        image_file (FileStorage): An optional new image file for the recipe.

    Returns:
        dict: Result indicating success or failure, with a message.
    """
    try:
        recipe = Recipe.query.get_or_404(id)

        # Update recipe details.
        recipe.title = title
        recipe.description = description

        # Handle image upload.
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            upload_folder = current_app.config["UPLOADED_PHOTOS_DEST"]
            file_path = os.path.join(upload_folder, filename)
            image_file.save(file_path)
            recipe.image = "uploads/images/" + filename

        # Update ingredients.
        ingredients = json.loads(ingredients_json)
        RecipeIngredient.query.filter_by(recipe_id=recipe.id).delete()

        for ingredient_data in ingredients:
            ingredient_name = ingredient_data["name"]
            ingredient = Ingredient.query.filter_by(
                name_ingredient=ingredient_name
            ).first()

            if not ingredient:
                ingredient = Ingredient(name_ingredient=ingredient_name)
                db.session.add(ingredient)
                db.session.flush()

            new_recipe_ingredient = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ingredient.id,
                quantity=ingredient_data["quantity"],
                unit=ingredient_data["unit"],
            )
            db.session.add(new_recipe_ingredient)

        db.session.commit()
        return {"error": False, "message": "Recipe updated successfully."}

    except Exception as e:
        return {"error": True, "message": str(e)}


def rate_recipe(recipe_id, user_id, stars):
    """
    Add or update a rating for a recipe.

    Args:
        recipe_id (int): The ID of the recipe to rate.
        user_id (int): The ID of the user providing the rating.
        stars (int): The rating score (1 to 5).

    Returns:
        dict: Result indicating success or failure, with a message.
    """
    try:
        if stars < 1 or stars > 5:
            return {"error": True, "message": "The rating must be between 1 and 5."}

        # Check if the user already rated the recipe.
        existing_rating = Rating.query.filter_by(
            recipe_id=recipe_id, user_id=user_id
        ).first()
        if existing_rating:
            existing_rating.stars = stars
            message = "Your rating has been updated."
        else:
            new_rating = Rating(stars=stars, recipe_id=recipe_id, user_id=user_id)
            db.session.add(new_rating)
            message = "Your rating has been added."

        db.session.commit()
        return {"error": False, "message": message}

    except Exception as e:
        db.session.rollback()
        return {"error": True, "message": str(e)}
