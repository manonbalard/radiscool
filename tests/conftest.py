import pytest
from myflaskapp import create_app
from extensions import configure_extensions, db
from models.models_sql import User


@pytest.fixture
def test_app():
    """
    Fixture to create the Flask application for testing.

    This sets up the application with the testing configuration, initializes
    the necessary extensions, and creates the database tables before running tests.
    """
    app = create_app(config_name="testing")  # Create the app with test configuration

    # Initialize extensions for the test application
    with app.app_context():
        configure_extensions(
            app
        )  # Ensure login_manager and other extensions are initialized
        db.create_all()  # Create all tables before starting the tests

    yield app  # Provide the app instance for tests

    # Cleanup after tests (remove session, drop database, etc.)
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def test_client(test_app):
    """
    Fixture to provide a test client for making HTTP requests.

    This allows tests to simulate HTTP requests to the application.
    """
    return test_app.test_client()


@pytest.fixture
def user(test_app):
    """
    Fixture to create a user in the database and return it.

    This ensures that a test user exists before running tests that require authentication.
    """
    with test_app.app_context():
        # Create a test user
        user = User(email="test@example.com", password="password")
        db.session.add(user)
        db.session.commit()  # Save the user to the database
        db.session.refresh(
            user
        )  # Ensure the user is properly associated with the session
    return user
