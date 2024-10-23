from extensions import db
from flask_login import UserMixin

class RecipeIngredient(db.Model):
    __tablename__ = 'recipe_ingredient'
    
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), primary_key=True)
    quantity = db.Column(db.Float)  
    unit = db.Column(db.String(20))

    # Relations
    recipe = db.relationship('Recipe', back_populates='ingredients')
    ingredient = db.relationship('Ingredient', back_populates='recipes')


class Recipe(db.Model):
    __tablename__ = 'recipe'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    image = db.Column(db.String(256))  

    ingredients = db.relationship('RecipeIngredient', back_populates='recipe')

class Ingredient(db.Model):
    __tablename__ = 'ingredient'  
    id = db.Column(db.Integer, primary_key=True)
    name_ingredient = db.Column(db.String(128), nullable=False)

    # Relation avec RecipeIngredient
    recipes = db.relationship('RecipeIngredient', back_populates='ingredient')

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(255))
    recipes = db.relationship('Recipe', backref='user', lazy=True)

    # Relation avec les évaluations 
    ratings = db.relationship('Rating', backref='user', lazy=True)

class Rating(db.Model):
    __tablename__ = 'rating'
    id = db.Column(db.Integer, primary_key=True)
    stars = db.Column(db.Integer, nullable=False)  # Nombre d'étoiles
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
