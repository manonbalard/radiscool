import pytest
from myflaskapp import app, db
from models.models_sql import User, Recipe, Ingredient, RecipeIngredient, Rating

@pytest.fixture(scope="module")
def test_client():
    # Crée un client de test à partir de l'application Flask existante
    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
        yield testing_client
        with app.app_context():
            db.session.remove()
            db.drop_all()


@pytest.fixture(scope="function")
def session():
    # Utilise la session actuelle pour les tests et la restaure après chaque test
    with app.app_context():
        yield db.session
        db.session.rollback()


def test_user_model(session):
    user = User(username="testuser", email="test@example.com", password="password")
    session.add(user)
    session.commit()

    retrieved_user = User.query.filter_by(username="testuser").first()
    assert retrieved_user is not None
    assert retrieved_user.email == "test@example.com"


def test_recipe_model(session):
    user = User(username="chef", email="chef@example.com", password="password")
    session.add(user)
    session.commit()

    recipe = Recipe(title="Tarte aux pommes", description="Délicieuse tarte aux pommes", user_id=user.id)
    session.add(recipe)
    session.commit()

    retrieved_recipe = Recipe.query.filter_by(title="Tarte aux pommes").first()
    assert retrieved_recipe is not None
    assert retrieved_recipe.description == "Délicieuse tarte aux pommes"
    assert retrieved_recipe.user.username == "chef"


def test_ingredient_model(session):
    ingredient = Ingredient(name_ingredient="Sucre")
    session.add(ingredient)
    session.commit()

    retrieved_ingredient = Ingredient.query.filter_by(name_ingredient="Sucre").first()
    assert retrieved_ingredient is not None


def test_recipe_ingredient_relationship(session):
    user = User(username="baker", email="baker@example.com", password="password")
    session.add(user)
    session.commit()

    recipe = Recipe(title="Gâteau au chocolat", description="Riche et moelleux", user_id=user.id)
    ingredient = Ingredient(name_ingredient="Chocolat")
    session.add_all([recipe, ingredient])
    session.commit()

    recipe_ingredient = RecipeIngredient(
        recipe_id=recipe.id,
        ingredient_id=ingredient.id,
        quantity=200.0,
        unit="grammes"
    )
    session.add(recipe_ingredient)
    session.commit()

    retrieved_recipe = Recipe.query.filter_by(title="Gâteau au chocolat").first()
    assert retrieved_recipe.ingredients[0].ingredient.name_ingredient == "Chocolat"


def test_rating_model(session):
    user = User(username="critic", email="critic@example.com", password="password")
    session.add(user)
    session.commit()

    recipe = Recipe(title="Soupe à l'oignon", description="Classique français", user_id=user.id)
    session.add(recipe)
    session.commit()

    rating = Rating(stars=5, recipe_id=recipe.id, user_id=user.id)
    session.add(rating)
    session.commit()

    retrieved_rating = Rating.query.filter_by(recipe_id=recipe.id, user_id=user.id).first()
    assert retrieved_rating is not None
    assert retrieved_rating.stars == 5
