from werkzeug.security import generate_password_hash, check_password_hash
from models.models_sql import User
from extensions import db
from flask_login import login_user


class UserService:
    """
    A service class for handling user-related operations such as creation, authentication,
    and login/logout functionality.
    """

    @staticmethod
    def create_user(username, email, password):
        """
        Create a new user in the system.

        Args:
            username (str): The username of the new user.
            email (str): The email address of the new user.
            password (str): The password of the new user.

        Returns:
            User: The newly created User object.

        Raises:
            ValueError: If the password is too weak or the email already exists.
        """
        # Check the strength of the password.
        if len(password) < 6:
            raise ValueError("Password is too weak")

        # Check if the email is already registered.
        if User.query.filter_by(email=email).first():
            raise ValueError("Email address already exists")

        # Hash the password for secure storage.
        hashed_password = generate_password_hash(
            password, method="pbkdf2:sha256", salt_length=16
        )

        # Create a new User instance.
        new_user = User(email=email, username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return new_user

    @staticmethod
    def authenticate_user(email, password):
        """
        Authenticate a user based on their email and password.

        Args:
            email (str): The email address of the user.
            password (str): The password provided for authentication.

        Returns:
            User: The authenticated User object.

        Raises:
            ValueError: If the email is not found or the password is incorrect.
        """
        # Retrieve the user by email.
        user = User.query.filter_by(email=email).first()

        if not user:
            raise ValueError("Email not found")

        # Verify the password against the stored hash.
        if not check_password_hash(user.password, password):
            raise ValueError("Password incorrect")

        return user

    @staticmethod
    def login_user(user, remember=False):
        """
        Log in the authenticated user.

        Args:
            user (User): The User object to log in.
            remember (bool): Whether to remember the user's session (default is False).
        """
        login_user(user, remember=remember)

    @staticmethod
    def logout_user(logout_function):
        """
        Log out the current user.

        Args:
            logout_function (callable): The function to execute for logging out.
        """
        logout_function()
