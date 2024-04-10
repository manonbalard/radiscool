from flask import Flask, render_template
from flask_login import LoginManager
from database import db
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'users.login'
    login_manager.init_app(app)

    from models.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from routes.recipes_bp import recipes as recipes_blueprint
    app.register_blueprint(recipes_blueprint, url_prefix='/recipes')

    from routes.users_bp import users as users_blueprint
    app.register_blueprint(users_blueprint, url_prefix='/users' )

    return app

app = create_app(Config) 

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
