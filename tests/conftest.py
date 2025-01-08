import os
import tempfile
import pytest
from myflaskapp import create_app, db
from models.models_sql import User

@pytest.fixture(scope='module')
def test_app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',  # Utilise une base de données en mémoire pour les tests
        'WTF_CSRF_ENABLED': False,  # Désactive CSRF pour les tests
    })
    db.init_app(app)

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def test_client(test_app):
    return test_app.test_client()

@pytest.fixture(scope='function')
def session(test_app):
    connection = db.engine.connect()
    transaction = connection.begin()
    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    yield session

    transaction.rollback()
    connection.close()
    session.remove()

@pytest.fixture
def user(test_app):
    with app.app_context():
        user = User(email='test@example.com', password='password')
        db.session.add(user)
        db.session.commit()
        return user