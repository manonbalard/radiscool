from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    Blueprint,
)
from flask_login import login_required, current_user
from models.models_sql import Recipe, RecipeIngredient
from services.recipe_service import (
    add_recipe,
    get_recipe_with_comments,
    delete_recipe,
    edit_recipe,
    rate_recipe,
)
from services.ingredient_service import (
    add_ingredient_to_recipe,
    delete_ingredient,
    update_ingredient,
)
from services.comment_service import add_comment, delete_comment

# Create a blueprint for recipe-related routes
recipes = Blueprint("recipes", __name__)


@recipes.route("/addrecipe", methods=["GET"])
def addrecipe():
    """
    Render the template for adding a new recipe.

    Returns:
        Rendered HTML template.
    """
    return render_template("recipes/add_recipe.html")


@recipes.route("/addrecipe_with_ingredients", methods=["POST"])
@login_required
def addrecipe_with_ingredients():
    """
    Handle the creation of a recipe with its associated ingredients.

    Returns:
        JSON response with the redirection URL or an error message.
    """
    title = request.form["title"]
    description = request.form["description"]
    ingredients = request.form["ingredients"]  # JSON string

    # Call the service to add the recipe
    result = add_recipe(
        title,
        description,
        ingredients,
        current_user.id,
        request.files.get("recipeImage"),
    )

    if result["error"]:
        flash(result["message"], "danger")
        return redirect(url_for("recipes.addrecipe"))

    return jsonify(
        {"redirect": url_for("recipes.view_recipe_route", id=result["recipe_id"])}
    )


@recipes.route("/recipes/<int:id>", methods=["GET"])
def view_recipe_route(id):
    """
    Display the details of a specific recipe along with its comments.

    Args:
        id (int): The ID of the recipe.

    Returns:
        Rendered HTML template or redirection if the recipe is not found.
    """
    result = get_recipe_with_comments(id)

    if result["error"]:
        flash(result["message"], "danger")
        return redirect(url_for("recipes.index"))

    return render_template(
        "recipes/view_recipe.html", recipe=result["recipe"], comments=result["comments"]
    )


@recipes.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete_recipe_route(id):
    """
    Delete a specific recipe by its ID.

    Args:
        id (int): The ID of the recipe to delete.

    Returns:
        Redirect to the recipe index page.
    """
    result = delete_recipe(id)

    if result["error"]:
        flash(result["message"], "danger")
    else:
        flash(result["message"], "success")

    return redirect(url_for("recipes.index"))


@recipes.route(
    "/delete_ingredient/<int:recipe_id>/<int:ingredient_id>", methods=["POST"]
)
@login_required
def delete_ingredient_route(recipe_id, ingredient_id):
    """
    Delete an ingredient from a recipe.

    Args:
        recipe_id (int): The ID of the recipe.
        ingredient_id (int): The ID of the ingredient to delete.

    Returns:
        JSON response with a success or error message.
    """
    result = delete_ingredient(recipe_id, ingredient_id)

    return jsonify({"message": result["message"]}), 200 if not result["error"] else 400


@recipes.route("/edit_recipe/<int:id>", methods=["GET", "POST"])
@login_required
def edit_recipe_route(id):
    """
    Edit an existing recipe.

    Args:
        id (int): The ID of the recipe to edit.

    Returns:
        Rendered template for GET requests or a redirect for POST requests.
    """
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        ingredients = request.form.get("ingredients", "[]")
        image_file = request.files.get("recipeImage")

        result = edit_recipe(id, title, description, ingredients, image_file)

        if result["error"]:
            flash(result["message"], "danger")
            return redirect(url_for("recipes.edit_recipe_route", id=id))

        flash("Recipe updated successfully.", "success")
        return redirect(url_for("recipes.view_recipe_route", id=id))

    recipe = Recipe.query.get(id)
    if not recipe:
        flash("The requested recipe was not found.", "danger")
        return redirect(url_for("recipes.index"))

    ingredients = RecipeIngredient.query.filter_by(recipe_id=recipe.id).all()
    return render_template(
        "recipes/edit_recipe.html", recipe=recipe, ingredients=ingredients
    )


@recipes.route("/edit_ingredient/<int:recipe_id>/<int:ingredient_id>", methods=["POST"])
@login_required
def edit_ingredient_route(recipe_id, ingredient_id):
    """
    Update the quantity and unit of a specific ingredient in a recipe.

    Args:
        recipe_id (int): The ID of the recipe.
        ingredient_id (int): The ID of the ingredient.

    Returns:
        JSON response with a success or error message.
    """
    data = request.get_json()
    quantity = data.get("quantity")
    unit = data.get("unit")

    result = update_ingredient(recipe_id, ingredient_id, quantity, unit)

    return jsonify({"message": result["message"]}), 200 if not result["error"] else 400


@recipes.route("/add_ingredient/<int:recipe_id>", methods=["POST"])
@login_required
def add_ingredient_route(recipe_id):
    """
    Add a new ingredient to a recipe.

    Args:
        recipe_id (int): The ID of the recipe to add the ingredient to.

    Returns:
        JSON response with ingredient details or an error message.
    """
    name_ingredient = request.form.get("name_ingredient")
    quantity = request.form.get("quantity")
    unit = request.form.get("unit")

    # Convert the quantity to float (if it is a valid number)
    try:
        quantity = float(quantity) if quantity else 0.0
    except ValueError:
        return (
            jsonify({"error": {"quantity": "The quantity must be a valid number."}}),
            400,
        )

    result = add_ingredient_to_recipe(recipe_id, name_ingredient, quantity, unit)

    if result["error"]:
        return jsonify({"error": result["message"]}), 400
    return (
        jsonify(
            {
                "id": result["ingredient_id"],
                "name_ingredient": name_ingredient,
                "quantity": quantity,
                "unit": unit,
                "message": result["message"],
            }
        ),
        200,
    )


@recipes.route("/get_ingredients/<int:recipe_id>", methods=["GET"])
def get_ingredients(recipe_id):
    """
    Retrieve all ingredients for a specific recipe.

    Args:
        recipe_id (int): The ID of the recipe.

    Returns:
        JSON response with a list of ingredients.
    """
    recipe = Recipe.query.get_or_404(recipe_id)
    ingredients = [
        {
            "id": ri.ingredient.id,
            "name": ri.ingredient.name_ingredient,
            "quantity": ri.quantity,
            "unit": ri.unit,
        }
        for ri in recipe.ingredients
    ]

    return jsonify(ingredients), 200


@recipes.route("/")
def index():
    """
    Display the index page with a list of all recipes, including their average ratings and comments.

    Returns:
        Rendered HTML template with the list of recipes.
    """
    all_recipes = Recipe.query.all()

    recipes_with_comments_and_ratings = [
        {
            "id": recipe.id,
            "title": recipe.title,
            "image": recipe.image,
            "average_rating": recipe.average_rating,
            "comments": recipe.get_comments(),
        }
        for recipe in all_recipes
    ]

    return render_template(
        "recipes/recipes.html", recipes=recipes_with_comments_and_ratings
    )


@recipes.route("/<int:recipe_id>/add_comment", methods=["POST"])
@login_required
def add_comment_route(recipe_id):
    """
    Add a comment to a recipe.

    Args:
        recipe_id (int): The ID of the recipe.

    Returns:
        JSON response with a success or error message.
    """
    text = request.form.get("comment")

    if not text:
        return jsonify({"error": "Comment cannot be empty"}), 400

    result = add_comment(recipe_id, current_user.id, text)

    if result["error"]:
        return jsonify({"error": result["message"]}), 400
    return jsonify({"message": result["message"]}), 201


@recipes.route("/comments/delete/<comment_id>", methods=["POST"])
@login_required
def delete_comment_route(comment_id):
    """
    Delete a specific comment by its ID.

    Args:
        comment_id (str): The ID of the comment to delete.

    Returns:
        JSON response with a success or error message.
    """
    result = delete_comment(comment_id)

    if result["error"]:
        return jsonify({"error": result["message"]}), 400
    return (jsonify({"message": result["message"]}),)


@recipes.route("/recipes/rate/<int:recipe_id>", methods=["POST"])
@login_required
def rate_recipe_route(recipe_id):
    """
    Rate a recipe with a number of stars.

    Args:
        recipe_id (int): The ID of the recipe to rate.

    Returns:
        Redirect to the recipe index page.
    """
    try:
        stars = int(request.form.get("stars"))
        result = rate_recipe(recipe_id=recipe_id, user_id=current_user.id, stars=stars)

        if result["error"]:
            flash(result["message"], "danger")
        else:
            flash(result["message"], "success")

    except ValueError:
        flash("Invalid value for rating.", "danger")

    return redirect(url_for("recipes.index"))
