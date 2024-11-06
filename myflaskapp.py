import os
from flask import Flask, render_template
from extensions import db, migrate, login_manager, photos, configure_extensions

# Configuration Setup
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = "Secret Key"
    SQLALCHEMY_DATABASE_URI = 'mysql://root:''@localhost/radiscool_test'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOADED_PHOTOS_DEST = os.path.join(basedir, 'static', 'uploads', 'images')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MONGO_URI = "mongodb://localhost:27017/Radiscool"

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

# Main Entry Point
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
