from extensions import db, mongo_db
from flask_login import UserMixin


class RecipeIngredient(db.Model):
    __tablename__ = "recipe_ingredient"

    recipe_id = db.Column(
        db.Integer, db.ForeignKey("recipe.id", ondelete="CASCADE"), primary_key=True
    )
    ingredient_id = db.Column(
        db.Integer, db.ForeignKey("ingredient.id", ondelete="CASCADE"), primary_key=True
    )
    quantity = db.Column(db.Float)
    unit = db.Column(db.String(20))

    # Relations
    recipe = db.relationship(
        "Recipe", back_populates="ingredients", passive_deletes=True
    )
    ingredient = db.relationship(
        "Ingredient", back_populates="recipes", passive_deletes=True
    )


class Recipe(db.Model):
    __tablename__ = "recipe"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    image = db.Column(db.String(256))

    ingredients = db.relationship("RecipeIngredient", back_populates="recipe")

    # Méthode pour récupérer les commentaires associés
    def get_comments(self):
        recipe_comments = mongo_db.comments.find({"recipe_id": self.id})
        comments_with_usernames = []
        for comment in recipe_comments:
            user = User.query.get(comment["user_id"])
            comment["username"] = user.username if user else "Utilisateur inconnu"
            comments_with_usernames.append(comment)
        return comments_with_usernames

    # Propriété calculée pour la moyenne des notes
    @property
    def average_rating(self):
        ratings = Rating.query.filter_by(recipe_id=self.id).all()
        if not ratings:
            return None  # Pas encore de notes
        return sum(r.stars for r in ratings) / len(ratings)


class Ingredient(db.Model):
    __tablename__ = "ingredient"
    id = db.Column(db.Integer, primary_key=True)
    name_ingredient = db.Column(db.String(128), nullable=False)

    # Relation avec RecipeIngredient
    recipes = db.relationship("RecipeIngredient", back_populates="ingredient")


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(255))
    recipes = db.relationship("Recipe", backref="user", lazy=True)

    # Relation avec les évaluations
    ratings = db.relationship("Rating", backref="user", lazy=True)


class Rating(db.Model):
    __tablename__ = "rating"
    id = db.Column(db.Integer, primary_key=True)
    stars = db.Column(db.Integer, nullable=False)  # Nombre d'étoiles
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
