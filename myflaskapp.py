import os
from flask import Flask, render_template
from flask_apscheduler import APScheduler
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

    # APScheduler configuration
    SCHEDULER_API_ENABLED = True

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

# Backup Functions
def backup_mysql():
    """Backup the MySQL database."""
    db_name = os.getenv("MYSQL_DB_NAME")
    db_user = os.getenv("MYSQL_USER")
    db_password = os.getenv("MYSQL_PASSWORD")
    backup_dir = os.path.join(basedir, "backups")
    os.makedirs(backup_dir, exist_ok=True)
    output_file = os.path.join(backup_dir, f"mysql_backup_{db_name}.sql")
    
    command = f"mysqldump -u {db_user} -p{db_password} {db_name} > {output_file}"
    os.system(command)
    print(f"MySQL backup saved to {output_file}")

def backup_mongo():
    """Backup the MongoDB database."""
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB_NAME")
    backup_dir = os.path.join(basedir, "backups")
    os.makedirs(backup_dir, exist_ok=True)
    output_dir = os.path.join(backup_dir, f"mongo_backup_{db_name}")
    
    command = f"mongodump --uri={mongo_uri} --db={db_name} --out={output_dir}"
    os.system(command)
    print(f"MongoDB backup saved to {output_dir}")

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
    app.run(host="0.0.0.0", debug=True)

def create_app(config_name='testing'):
    app = Flask(__name__)
    app.config.from_object(config_name)
    app.register_blueprint(recipes)
    app.register_blueprint(users)
    return app
