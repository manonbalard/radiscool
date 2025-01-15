from myflaskapp import db
from models.models_sql import User, Recipe, Ingredient, RecipeIngredient, Rating


# Test for the User model
def test_user_model(test_client, user):
    """Test the User model to ensure it functions correctly."""
    with test_client.application.app_context():
        # Retrieve the user created by the 'user' fixture
        retrieved_user = User.query.filter_by(email="test@example.com").first()
        # Check that the user exists
        assert retrieved_user is not None
        # Verify that the email is correct
        assert retrieved_user.email == "test@example.com"


# Test for the Recipe model
def test_recipe_model(test_client):
    """Test the Recipe model to ensure it functions correctly."""
    with test_client.application.app_context():
        # Create a user to associate with the recipe
        user = User(email="test@example.com", password="password")
        db.session.add(user)
        db.session.commit()

        # Create a recipe associated with this user
        recipe = Recipe(
            title="Tarte aux pommes",
            description="Délicieuse tarte aux pommes",
            user_id=user.id,
        )
        db.session.add(recipe)
        db.session.commit()

        # Check that the recipe can be retrieved correctly
        retrieved_recipe = Recipe.query.filter_by(title="Tarte aux pommes").first()
        assert retrieved_recipe is not None
        assert retrieved_recipe.description == "Délicieuse tarte aux pommes"


# Test for the Ingredient model
def test_ingredient_model(test_client, user):
    """Test the Ingredient model to ensure it functions correctly."""
    with test_client.application.app_context():
        # Create an ingredient
        ingredient = Ingredient(name_ingredient="Sucre")
        db.session.add(ingredient)
        db.session.commit()

        # Check that the ingredient is correctly retrieved
        retrieved_ingredient = Ingredient.query.filter_by(
            name_ingredient="Sucre"
        ).first()
        assert retrieved_ingredient is not None


# Test the relationship between Recipe and Ingredient
def test_recipe_ingredient_relationship(test_client, user):
    """Test the relationship between Recipe and Ingredient models."""
    with test_client.application.app_context():
        # Create a user for the recipe
        user = User(username="baker", email="baker@example.com", password="password")
        db.session.add(user)
        db.session.commit()

        # Create a recipe and an ingredient
        recipe = Recipe(
            title="Gâteau au chocolat", description="Riche et moelleux", user_id=user.id
        )
        ingredient = Ingredient(name_ingredient="Chocolat")
        db.session.add_all([recipe, ingredient])
        db.session.commit()

        # Create a relationship between the recipe and the ingredient
        recipe_ingredient = RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_id=ingredient.id,
            quantity=200.0,
            unit="grammes",
        )
        db.session.add(recipe_ingredient)
        db.session.commit()

        # Check that the ingredient is correctly associated with the recipe
        retrieved_recipe = Recipe.query.filter_by(title="Gâteau au chocolat").first()
        assert retrieved_recipe.ingredients[0].ingredient.name_ingredient == "Chocolat"


# Test for the Rating model
def test_rating_model(test_client, user):
    """Test the Rating model to ensure it functions correctly."""
    with test_client.application.app_context():
        # Create a user for the rating
        user = User(username="critic", email="critic@example.com", password="password")
        db.session.add(user)
        db.session.commit()

        # Create a recipe to rate
        recipe = Recipe(
            title="Soupe à l'oignon", description="Classique français", user_id=user.id
        )
        db.session.add(recipe)
        db.session.commit()

        # Crée une note associée à la recette et l'utilisateur
        rating = Rating(stars=5, recipe_id=recipe.id, user_id=user.id)
        db.session.add(rating)
        db.session.commit()

        # Create a rating associated with the recipe and user
        rating = Rating(stars=5, recipe_id=recipe.id, user_id=user.id)
        db.session.add(rating)
        db.session.commit()

        # Check that the rating is correctly saved
        retrieved_rating = Rating.query.filter_by(
            recipe_id=recipe.id, user_id=user.id
        ).first()
    assert retrieved_rating is not None
    assert retrieved_rating.stars == 5
