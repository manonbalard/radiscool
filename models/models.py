from extensions import db
from flask_login import UserMixin
from datetime import datetime

# Table d'association Recipe_Ingredient pour la relation many-to-many
recipe_ingredient = db.Table('recipe_ingredient',
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id'), primary_key=True),
    db.Column('ingredient_id', db.Integer, db.ForeignKey('ingredient.id'), primary_key=True),
    db.Column('quantity', db.Float, nullable=False),  # Quantité de l'ingrédient dans la recette
    db.Column('unit', db.String(100), nullable=False)  # Unité de mesure (grammes, litres, etc.)
)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relation many-to-many avec Ingredient via la table recipe_ingredient
    ingredients = db.relationship('Ingredient', secondary=recipe_ingredient, lazy='subquery',
                                  backref=db.backref('recipes', lazy=True))

    # Relation avec les commentaires et évaluations
    comments = db.relationship('Comment', backref='recipe', lazy=True)
    ratings = db.relationship('Rating', backref='recipe', lazy=True)

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_ingredient = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name_ingredient': self.name_ingredient
        }

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    recipes = db.relationship('Recipe', backref='user', lazy=True)

    # Relation avec les commentaires et évaluations
    comments = db.relationship('Comment', backref='user', lazy=True)
    ratings = db.relationship('Rating', backref='user', lazy=True)

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stars = db.Column(db.Integer, nullable=False)  # Nombre d'étoiles
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)  # Contenu du commentaire
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Date du commentaire
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
