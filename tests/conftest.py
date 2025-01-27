import pytest
from myflaskapp import create_app
from extensions import configure_extensions, db
from models.models_sql import User


@pytest.fixture
def test_app():
    """Fixture pour créer l'application Flask pour les tests."""
    app = create_app(config_name="testing")  # Crée l'application avec la config de test

    # Initialisez les extensions pour l'application de test
    with app.app_context():
        configure_extensions(app)  # Assurez-vous que login_manager est bien initialisé
        db.create_all()  # Crée toutes les tables avant de commencer les tests

    yield app  # Cette ligne permet d'utiliser l'application dans les tests

    # Nettoyez après les tests (fermez la session, etc.)
    with app.app_context():
        db.session.remove()
        db.drop_all()  # Optionnel, si vous voulez effacer la base de données après chaque test


# Fixture pour le client de test (utilisé pour faire des requêtes HTTP)
@pytest.fixture
def test_client(test_app):
    return test_app.test_client()


@pytest.fixture
def user(test_app):
    """Fixture pour créer un utilisateur dans la base de données et le connecter."""
    with test_app.app_context():
        # Créer l'utilisateur
        user = User(email="test@example.com", password="password")
        db.session.add(user)
        db.session.commit()  # Sauvegarde dans la base de données
        db.session.refresh(user)  # Assure que l'utilisateur est bien lié à la session
    return user
