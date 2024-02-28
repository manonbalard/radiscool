from database import db
from flask_login import Mixin
from werkzeug.security import generate_password_hash, check_password_hash

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(255), nullable = False)
    ingredients = db.relationship('Ingredient', backref='recipe', lazy=True)
    description = db.Column(db.Text, nullable=False)

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    quantity = db.Column(db.Float, nullable = False)
    unit = db.Column(db.String(100), nullable = False)
    name_ingredient = db.Column(db.String(255), nullable = False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable = False)
    
    def to_dict(self):
         return {
              'id': self.id,
              'quantity': self.quantity,
              'unit': self.unit,
              'name_ingredient': self.name_ingredient,
              'recipe_id': self.recipe_id
         }
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)

    recipes = db.relationship('Recipe', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
