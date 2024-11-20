import os
from flask import Flask, render_template
from extensions import db, migrate, login_manager, photos, configure_extensions
from dotenv import load_dotenv
load_dotenv()

# Configuration Setup
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOADED_PHOTOS_DEST = os.path.join(basedir, 'static', 'uploads', 'images')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MONGO_URI = os.getenv("MONGO_URI")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # Limite à 5 MB

# App Initialization
app = Flask(__name__)
app.config.from_object(Config)
migrate.init_app(app, db)
login_manager.init_app(app)

# Configure extensions
configure_extensions(app)

# Import models 
from models.models_sql import Recipe, Ingredient, User
from models.models_nosql import CommentNoSQL  

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Blueprint Registration
from routes.recipes_bp import recipes
app.register_blueprint(recipes, url_prefix='/recipes')

from routes.users_bp import users
app.register_blueprint(users, url_prefix='/users')

# Routes
@app.route('/')
def home():
    return render_template('home.html')

# Handle large file uploads gracefully
@app.errorhandler(413)
def request_entity_too_large(error):
    return "Le fichier est trop volumineux. La taille maximale est de 5 MB.", 413

# Main Entry Point
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
