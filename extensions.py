from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

# Initialize Flask extensions
db = SQLAlchemy()  # SQLAlchemy for database integration with SQL databases
migrate = Migrate()  # Flask-Migrate to handle database migrations
login_manager = LoginManager()  # Flask-Login for user authentication management
photos = UploadSet(
    "photos", IMAGES
)  # Flask-Uploads to manage uploaded files, specifically images

# Initialize MongoDB connection
client = MongoClient(
    "mongodb://localhost:27017/"
)  # Connect to MongoDB on the local host, port 27017
try:
    # Test if the connection to MongoDB is established by sending a ping
    client.admin.command("ping")  # Sending a ping to check if MongoDB responds
    print(
        "MongoDB connection successful!"
    )  # If the ping succeeds, the connection is established
except ServerSelectionTimeoutError as e:
    # Handle errors in case MongoDB is not accessible
    print(
        f"MongoDB connection error: {e}"
    )  # Display the error if MongoDB cannot be reached
mongo_db = client["Radiscool"]  # Select the "Radiscool" database in MongoDB


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
    configure_uploads(
        app, photos
    )  # Configure file uploads for photos with the Flask app

    # Ensure the upload directory exists, otherwise create it
    import os

    if not os.path.exists(
        app.config["UPLOADED_PHOTOS_DEST"]
    ):  # Check if the upload folder exists
        os.makedirs(
            app.config["UPLOADED_PHOTOS_DEST"]
        )  # Create the folder if it doesn't exist
