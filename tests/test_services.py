from unittest.mock import patch, MagicMock
from services.comment_service import add_comment, delete_comment, update_comment
from services.ingredient_service import (
    add_ingredient_to_recipe,
    delete_ingredient,
)
from services.recipe_service import add_recipe, delete_recipe, rate_recipe


# Comment Service Tests
@patch("services.comment_service.CommentNoSQL")
def test_add_comment(mock_comment):
    mock_comment.return_value.save = MagicMock()
    result = add_comment(recipe_id=1, user_id=1, text="Delicious!")
    assert result["error"] is False
    assert result["message"] == "Comment added."


@patch("services.comment_service.CommentNoSQL")
def test_delete_comment(mock_comment):
    mock_comment.delete_comment.return_value.deleted_count = 1
    result = delete_comment(comment_id=1)
    assert result["error"] is False
    assert result["message"] == "Comment deleted."


@patch("services.comment_service.CommentNoSQL")
def test_update_comment(mock_comment):
    mock_comment.update_comment.return_value.modified_count = 1
    result = update_comment(comment_id=1, new_text="Updated text")
    assert result["error"] is False
    assert result["message"] == "Comment updated."


# Ingredient Service Tests
@patch("services.ingredient_service.db.session")
@patch("services.ingredient_service.Ingredient")
@patch("services.ingredient_service.RecipeIngredient")
def test_add_ingredient_to_recipe(mock_recipe_ingredient, mock_ingredient, mock_db):
    mock_ingredient.query.filter_by.return_value.first.return_value = None
    mock_db.commit = MagicMock()
    result = add_ingredient_to_recipe(
        recipe_id=1, name_ingredient="Salt", quantity=1, unit="tsp"
    )
    assert result["error"] is False
    assert result["message"] == "Ingredient added successfully."


@patch("services.ingredient_service.db.session")
@patch("services.ingredient_service.RecipeIngredient")
def test_delete_ingredient(mock_recipe_ingredient, mock_db):
    mock_recipe_ingredient.query.filter_by.return_value.first_or_404.return_value = (
        MagicMock()
    )
    mock_db.commit = MagicMock()
    result = delete_ingredient(recipe_id=1, ingredient_id=1)
    assert result["error"] is False
    assert result["message"] == "Ingredient removed from recipe."


# Recipe Service Tests
@patch("services.recipe_service.db.session")
@patch("services.recipe_service.Recipe")
def test_add_recipe(mock_recipe, mock_db):
    mock_recipe.return_value.get_comments = MagicMock()
    mock_db.commit = MagicMock()
    result = add_recipe(
        title="Test Recipe",
        description="Test Description",
        ingredients_json='[{"name": "Salt", "quantity": 1, "unit": "tsp"}]',
        user_id=1,
        image_file=None,
    )
    assert result["error"] is False
    assert "recipe_id" in result


@patch("services.recipe_service.db.session")
@patch("services.recipe_service.Recipe")
def test_delete_recipe(mock_recipe, mock_db):
    mock_recipe.query.get_or_404.return_value = MagicMock()
    mock_db.commit = MagicMock()
    result = delete_recipe(id=1)
    assert result["error"] is False
    assert result["message"] == "Recipe and unused ingredients deleted."


@patch("services.recipe_service.db.session")
@patch("services.recipe_service.Rating")
def test_rate_recipe(mock_rating, mock_db):
    mock_rating.query.filter_by.return_value.first.return_value = None
    mock_db.commit = MagicMock()
    result = rate_recipe(recipe_id=1, user_id=1, stars=5)
    assert result["error"] is False
    assert "note" in result["message"]
