import pytest
from myflaskapp import create_app, db
from models.models_sql import User, Recipe, Ingredient, RecipeIngredient, Rating

# Test du modèle User
def test_user_model(test_client, user):
    """Test du modèle User"""
    with test_client.application.app_context():  # Assurez-vous d'avoir le contexte Flask
        # Récupération de l'utilisateur créé par la fixture 'user'
        retrieved_user = User.query.filter_by(email="test@example.com").first()
        # Vérifie que l'utilisateur existe
        assert retrieved_user is not None
        # Vérifie que l'email est correct
        assert retrieved_user.email == "test@example.com"

# Test du modèle Recipe
def test_recipe_model(test_client):
    """Test du modèle Recipe"""
    with test_client.application.app_context():
        # Crée un utilisateur pour associer la recette
        user = User(email='test@example.com', password='password')
        db.session.add(user)
        db.session.commit()
        
        # Crée une recette associée à cet utilisateur
        recipe = Recipe(title="Tarte aux pommes", description="Délicieuse tarte aux pommes", user_id=user.id)
        db.session.add(recipe)
        db.session.commit()

        # Vérifie que la recette peut être récupérée correctement
        retrieved_recipe = Recipe.query.filter_by(title="Tarte aux pommes").first()
        assert retrieved_recipe is not None
        assert retrieved_recipe.description == "Délicieuse tarte aux pommes"

# Test du modèle Ingredient
def test_ingredient_model(test_client, user):
    with test_client.application.app_context():  # Assurez-vous d'avoir le contexte Flask
        # Crée un ingrédient
        ingredient = Ingredient(name_ingredient="Sucre")
        db.session.add(ingredient)
        db.session.commit()

        # Vérifie que l'ingrédient est correctement récupéré
        retrieved_ingredient = Ingredient.query.filter_by(name_ingredient="Sucre").first()
        assert retrieved_ingredient is not None

# Test de la relation entre Recipe et Ingredient
def test_recipe_ingredient_relationship(test_client, user):
    with test_client.application.app_context():  # Assurez-vous d'avoir le contexte Flask
        # Crée un utilisateur pour la recette
        user = User(username="baker", email="baker@example.com", password="password")
        db.session.add(user)
        db.session.commit()

        # Crée une recette et un ingrédient
        recipe = Recipe(title="Gâteau au chocolat", description="Riche et moelleux", user_id=user.id)
        ingredient = Ingredient(name_ingredient="Chocolat")
        db.session.add_all([recipe, ingredient])
        db.session.commit()

        # Ajoute une relation entre la recette et l'ingrédient
        recipe_ingredient = RecipeIngredient(
        recipe_id=recipe.id,
        ingredient_id=ingredient.id,
        quantity=200.0,
        unit="grammes"
    )
        db.session.add(recipe_ingredient)
        db.session.commit()

        # Vérifie que l'ingrédient est correctement associé à la recette
        retrieved_recipe = Recipe.query.filter_by(title="Gâteau au chocolat").first()
        assert retrieved_recipe.ingredients[0].ingredient.name_ingredient == "Chocolat"

# Test du modèle Rating
def test_rating_model(test_client, user):
    with test_client.application.app_context():  # Assurez-vous d'avoir le contexte Flask
        # Crée un utilisateur pour la note
        user = User(username="critic", email="critic@example.com", password="password")
        db.session.add(user)
        db.session.commit()

        # Crée une recette pour laquelle attribuer une note
        recipe = Recipe(title="Soupe à l'oignon", description="Classique français", user_id=user.id)
        db.session.add(recipe)
        db.session.commit()

        # Crée une note associée à la recette et l'utilisateur
        rating = Rating(stars=5, recipe_id=recipe.id, user_id=user.id)
        db.session.add(rating)
        db.session.commit()

        # Vérifie que la note est correctement enregistrée
        retrieved_rating = Rating.query.filter_by(recipe_id=recipe.id, user_id=user.id).first()
    assert retrieved_rating is not None
    assert retrieved_rating.stars == 5
