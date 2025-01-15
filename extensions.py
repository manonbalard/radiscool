from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
photos = UploadSet("photos", IMAGES)

# Initialiser la connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")
try:
    # Tester si la connexion est établie en essayant de lister les bases de données
    client.admin.command("ping")  # Envoi d'un ping à MongoDB pour tester la connexion
    print("Connexion MongoDB réussie!")
except ServerSelectionTimeoutError as e:
    print(f"Erreur de connexion à MongoDB : {e}")
mongo_db = client["Radiscool"]


# Function to configure extensions
def configure_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "users.login"
    configure_uploads(app, photos)

    # Ensure the upload directory exists
    import os

    if not os.path.exists(app.config["UPLOADED_PHOTOS_DEST"]):
        os.makedirs(app.config["UPLOADED_PHOTOS_DEST"])
