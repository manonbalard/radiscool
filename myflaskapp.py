import os
import subprocess  # nosec B404
from flask import Flask, render_template
from flask_apscheduler import APScheduler
from extensions import db, migrate, login_manager, configure_extensions
from dotenv import load_dotenv
from models.models_sql import User
from routes.recipes_bp import recipes
from routes.users_bp import users

# Load environment variables from a .env file
load_dotenv()

# Configuration Setup
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """
    Configuration class to store application settings and environment variables.

    Attributes:
        SECRET_KEY (str): Secret key for session management.
        SQLALCHEMY_DATABASE_URI (str): Database URI for SQLAlchemy.
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Disable SQLAlchemy modification tracking.
        UPLOADED_PHOTOS_DEST (str): Directory where uploaded photos will be stored.
        ALLOWED_EXTENSIONS (set): Set of allowed file extensions for uploads.
        MONGO_URI (str): URI for MongoDB connection.
        MAX_CONTENT_LENGTH (int): Maximum size for file uploads (5 MB).
        SCHEDULER_API_ENABLED (bool): Enable APScheduler API.
        SERVER_NAME (str): Server name for URL generation.
        PREFERRED_URL_SCHEME (str): Preferred URL scheme (HTTP/HTTPS).
    """

    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOADED_PHOTOS_DEST = os.path.join(basedir, "static", "uploads", "images")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
    MONGO_URI = os.getenv("MONGO_URI")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # Limit uploads to 5 MB

    # APScheduler configuration
    SCHEDULER_API_ENABLED = True

    # Additional configurations
    PREFERRED_URL_SCHEME = "http"  # Change to "https" if your app uses HTTPS


# App Initialization
app = Flask(__name__)  # Create the Flask app
app.config.from_object(Config)  # Load configuration from the Config class
migrate.init_app(app, db)  # Initialize database migrations
login_manager.init_app(app)  # Initialize login manager

# Configure extensions
configure_extensions(app)  # Set up extensions like database, uploads, etc.


@login_manager.user_loader
def load_user(user_id):
    """Load a user given their user_id."""
    return User.query.get(int(user_id))


# Blueprint Registration

# Register blueprints for the routes (recipes and users)
app.register_blueprint(recipes, url_prefix="/recipes")
app.register_blueprint(users, url_prefix="/users")


# Routes
@app.route("/")
def home():
    """Render the homepage."""
    return render_template("home.html")


# Handle large file uploads gracefully
@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle the error when a file exceeds the maximum allowed size."""
    return "The file is too large. The maximum size is 5 MB.", 413


# Paths to backup tools (mysqldump and mongodump)
mysqldump_path = "/usr/bin/mysqldump"
mongodump_path = "/usr/bin/mongodump"


# Backup Functions
def backup_mysql():
    """Backup the MySQL database."""
    db_name = os.getenv("MYSQL_DB_NAME")
    db_user = os.getenv("MYSQL_USER")
    db_password = os.getenv("MYSQL_PASSWORD")
    backup_dir = os.path.join(basedir, "backups")
    os.makedirs(
        backup_dir, exist_ok=True
    )  # Create the backup directory if it doesn't exist
    output_file = os.path.join(backup_dir, f"mysql_backup_{db_name}.sql")

    try:
        # Using subprocess to run the backup command securely
        with open(output_file, "w") as outfile:
            subprocess.run(
                [mysqldump_path, "-u", db_user, f"-p{db_password}", db_name],
                stdout=outfile,
                check=True,
            )  # nosec B603 B607
        print(f"MySQL backup saved to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error during MySQL backup: {e}")


def backup_mongo():
    """Backup the MongoDB database."""
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB_NAME")
    backup_dir = os.path.join(basedir, "backups")
    os.makedirs(
        backup_dir, exist_ok=True
    )  # Create the backup directory if it doesn't exist
    output_dir = os.path.join(backup_dir, f"mongo_backup_{db_name}")

    try:
        # Using subprocess to run the backup command securely
        subprocess.run(
            [
                mongodump_path,
                f"--uri={mongo_uri}",
                f"--db={db_name}",
                f"--out={output_dir}",
            ],
            check=True,
        )  # nosec B603 B607
        print(f"MongoDB backup saved to {output_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Error during MongoDB backup: {e}")


# Configure APScheduler for scheduled tasks
scheduler = APScheduler()


@scheduler.task("cron", id="backup_mysql_task", hour=2, minute=0)
def scheduled_mysql_backup():
    """Schedule MySQL backup at 2:00 AM every day."""
    backup_mysql()


@scheduler.task("cron", id="backup_mongo_task", hour=3, minute=0)
def scheduled_mongo_backup():
    """Schedule MongoDB backup at 3:00 AM every day."""
    backup_mongo()


# Initialize and start the APScheduler
scheduler.init_app(app)
scheduler.start()


# Main Entry Point
if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="localhost", debug=debug_mode)


class TestingConfig(Config):
    """Configuration spécifique à l'environnement de test."""

    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///:memory:"  # Exemple d'URL de base de données pour tests
    )
    SERVER_NAME = "localhost"  # Important pour la génération des URLs dans un test
    TESTING = True
    WTF_CSRF_ENABLED = False  # Désactiver CSRF pour les tests


def create_app(config_name="testing"):
    """
    Factory function to create the Flask app with a specified configuration.

    Args:
        config_name (str): The name of the configuration to load (default is "testing").

    Returns:
        Flask: The initialized Flask application.
    """
    app = Flask(__name__)
    app.config.from_object(TestingConfig)  # Load configuration

    # Ajouter la route home ici
    @app.route("/")
    def home():
        """Render the homepage."""
        return render_template("home.html")

    app.register_blueprint(recipes)  # Register the recipes blueprint
    app.register_blueprint(users)  # Register the users blueprint
    return app
