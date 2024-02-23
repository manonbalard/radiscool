from flask import Flask, render_template
from database import db
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    from recipes.routes import recipes as recipes_blueprint
    app.register_blueprint(recipes_blueprint, url_prefix='/recipes')

    return app

app = create_app(Config) 

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
