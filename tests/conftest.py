import pytest
from myflaskapp import create_app, db
from models.models_sql import User
import secrets  # Importation du module secrets pour générer une clé secrète sécurisée

# Fixture pour l'application de test
@pytest.fixture
def test_app():
    # Crée l'application Flask avec une configuration spécifique pour les tests
    app = create_app()
    
    # Génération d'une clé secrète aléatoire et sécurisée
    secret_key = secrets.token_hex(16)  # Crée une clé secrète de 32 caractères hexadécimaux
    
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',  # Base de données en mémoire pour tests
        'WTF_CSRF_ENABLED': False,  # Désactive CSRF pour les tests
        'SECRET_KEY': secret_key,  # Utilisation de la clé secrète générée
    })
    
    # Crée la base de données en mémoire avant chaque test
    with app.app_context():
        db.init_app(app)  # Assurez-vous que l'instance de db est initialisée
        db.create_all()
        yield app  # Donne l'application à utiliser pour le test
        db.session.remove()  # Enlève la session après le test
        db.drop_all()  # Détruit la base de données après chaque test

# Fixture pour le client de test (utilisé pour faire des requêtes HTTP)
@pytest.fixture
def test_client(test_app):
    return test_app.test_client()

# Fixture pour créer un utilisateur dans la base de données
@pytest.fixture
def user(test_app):
    # Crée un utilisateur dans la base de données pour les tests
    with test_app.app_context():
        user = User(email='test@example.com', password='password')
        db.session.add(user)
        db.session.commit()  # Sauvegarde dans la base de données
        return db.session.merge(user)  # Retourne l'utilisateur pour l'utiliser dans les tests
