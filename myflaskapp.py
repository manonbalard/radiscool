import os
import subprocess  # nosec B404
from flask import Flask, render_template
from flask_apscheduler import APScheduler
from extensions import db, migrate, login_manager, configure_extensions
from dotenv import load_dotenv
from models.models_sql import User
from routes.recipes_bp import recipes
from routes.users_bp import users

load_dotenv()

# Configuration Setup
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOADED_PHOTOS_DEST = os.path.join(basedir, "static", "uploads", "images")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
    MONGO_URI = os.getenv("MONGO_URI")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # Limite à 5 MB

    # APScheduler configuration
    SCHEDULER_API_ENABLED = True

    # Ajoutez les configurations suivantes
    SERVER_NAME = os.getenv(
        "SERVER_NAME", "localhost:5000"
    )  # Par défaut, utilise localhost:5000
    PREFERRED_URL_SCHEME = (
        "http"  # Remplacez par "https" si votre application utilise HTTPS
    )


# App Initialization
app = Flask(__name__)
app.config.from_object(Config)
migrate.init_app(app, db)
login_manager.init_app(app)

# Configure extensions
configure_extensions(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Blueprint Registration

app.register_blueprint(recipes, url_prefix="/recipes")
app.register_blueprint(users, url_prefix="/users")


# Routes
@app.route("/")
def home():
    return render_template("home.html")


# Handle large file uploads gracefully
@app.errorhandler(413)
def request_entity_too_large(error):
    return "Le fichier est trop volumineux. La taille maximale est de 5 MB.", 413


mysqldump_path = "/usr/bin/mysqldump"
mongodump_path = "/usr/bin/mongodump"


# Backup Functions
def backup_mysql():
    """Backup the MySQL database."""
    db_name = os.getenv("MYSQL_DB_NAME")
    db_user = os.getenv("MYSQL_USER")
    db_password = os.getenv("MYSQL_PASSWORD")
    backup_dir = os.path.join(basedir, "backups")
    os.makedirs(backup_dir, exist_ok=True)
    output_file = os.path.join(backup_dir, f"mysql_backup_{db_name}.sql")

    try:
        # Utilisation de subprocess pour exécuter la commande de manière sécurisée
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
    os.makedirs(backup_dir, exist_ok=True)
    output_dir = os.path.join(backup_dir, f"mongo_backup_{db_name}")

    try:
        # Utilisation de subprocess pour exécuter la commande de manière sécurisée
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


# Configure APScheduler
scheduler = APScheduler()


@scheduler.task("cron", id="backup_mysql_task", hour=2, minute=0)
def scheduled_mysql_backup():
    """Schedule MySQL backup at 2:00 AM every day."""
    backup_mysql()


@scheduler.task("cron", id="backup_mongo_task", hour=3, minute=0)
def scheduled_mongo_backup():
    """Schedule MongoDB backup at 3:00 AM every day."""
    backup_mongo()


scheduler.init_app(app)
scheduler.start()

# Main Entry Point
if __name__ == "__main__":
    host = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host=host, debug=debug_mode)


def create_app(config_name="testing"):
    app = Flask(__name__)
    app.config.from_object(config_name)
    app.register_blueprint(recipes)
    app.register_blueprint(users)
    return app
