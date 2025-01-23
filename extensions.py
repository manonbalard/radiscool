import os
from flask import current_app
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

# Initialize Flask extensions
db = SQLAlchemy()  # SQLAlchemy for database integration with SQL databases
migrate = Migrate()  # Flask-Migrate to handle database migrations
login_manager = LoginManager()  # Flask-Login for user authentication management

# Function to configure Flask extensions
def configure_extensions(app):
    """
    Configures and initializes necessary Flask extensions for the application.

    Args:
        app (Flask): The Flask application to configure.

    This function sets up all necessary extensions for the app, including
    database, migrations, user authentication, and file upload handling.
    """
    db.init_app(app)  # Initialize SQLAlchemy with the Flask application
    migrate.init_app(
        app, db
    )  # Initialize Flask-Migrate with the application and database
    login_manager.init_app(app)  # Initialize Flask-Login with the Flask application
    login_manager.login_view = (
        "users.login"  # Set the default login view for user authentication
    )

    # Ensure the upload directory exists, otherwise create it
    if not os.path.exists(app.config["UPLOADED_PHOTOS_DEST"]):
        os.makedirs(app.config["UPLOADED_PHOTOS_DEST"])


# Function to handle file uploads (images)
def save_uploaded_file(image_file):
    """
    Save the uploaded image file to the designated directory.

    Args:
        image_file (FileStorage): The uploaded image file from the request.

    Returns:
        str: The filename of the saved image.
    """
    if image_file:
        # Check if the file has a valid extension (you can extend this with more file types)
        allowed_extensions = {"jpg", "jpeg", "png", "gif", "bmp", "tiff"}
        filename = secure_filename(image_file.filename)
        file_extension = filename.rsplit(".", 1)[-1].lower()

        # Check if file extension is valid
        if file_extension not in allowed_extensions:
            raise ValueError("File type is not allowed. Only image files are accepted.")

        # Save the file to the designated folder
        file_path = os.path.join(current_app.config["UPLOADED_PHOTOS_DEST"], filename)
        image_file.save(file_path)

        return filename
    return None
