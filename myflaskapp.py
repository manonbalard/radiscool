import os
from flask import Flask, render_template
from database import db, migrate
from flask_login import LoginManager

# Configuration Setup
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = "Secret Key"
    SQLALCHEMY_DATABASE_URI = 'mysql://root:''@localhost/radiscool'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# App Initialization
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate.init_app(app, db)

# Import models after db is initialized
from models.models import Recipe, Ingredient, User

# Login Manager Setup
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Blueprint Registration
from routes.recipes_bp import recipes as recipes_blueprint
app.register_blueprint(recipes_blueprint, url_prefix='/recipes')

from routes.users_bp import users as users_blueprint
app.register_blueprint(users_blueprint, url_prefix='/users')

# Configuration
UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

# Routes
@app.route('/')
def home():
    return render_template('home.html')

# Main Entry Point
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
