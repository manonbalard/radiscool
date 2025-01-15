from extensions import db, mongo_db
from flask_login import UserMixin


class RecipeIngredient(db.Model):
    """Represents the association between a recipe and its ingredients."""

    __tablename__ = "recipe_ingredient"

    # Foreign keys to the recipe and ingredient tables
    recipe_id = db.Column(
        db.Integer, db.ForeignKey("recipe.id", ondelete="CASCADE"), primary_key=True
    )
    ingredient_id = db.Column(
        db.Integer, db.ForeignKey("ingredient.id", ondelete="CASCADE"), primary_key=True
    )
    quantity = db.Column(db.Float)  # Quantity of the ingredient in the recipe
    unit = db.Column(db.String(20))  # Unit of measurement for the ingredient

    # Relationships to Recipe and Ingredient models
    recipe = db.relationship(
        "Recipe", back_populates="ingredients", passive_deletes=True
    )
    ingredient = db.relationship(
        "Ingredient", back_populates="recipes", passive_deletes=True
    )


class Recipe(db.Model):
    """Represents a recipe in the system."""

    __tablename__ = "recipe"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)  # Title of the recipe
    description = db.Column(db.Text)  # Description of the recipe
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id")
    )  # User who created the recipe
    image = db.Column(db.String(256))  # Image associated with the recipe

    # Relationship with RecipeIngredient model
    ingredients = db.relationship("RecipeIngredient", back_populates="recipe")

    def get_comments(self):
        """Retrieve all comments associated with this recipe."""
        recipe_comments = mongo_db.comments.find({"recipe_id": self.id})
        comments_with_usernames = []
        for comment in recipe_comments:
            user = User.query.get(comment["user_id"])
            comment["username"] = user.username if user else "Unknown user"
            comments_with_usernames.append(comment)
        return comments_with_usernames

    @property
    def average_rating(self):
        """Calculate the average rating for this recipe."""
        ratings = Rating.query.filter_by(recipe_id=self.id).all()
        if not ratings:
            return None  # No ratings yet
        return sum(r.stars for r in ratings) / len(ratings)


class Ingredient(db.Model):
    """Represents an ingredient used in recipes."""

    __tablename__ = "ingredient"
    id = db.Column(db.Integer, primary_key=True)
    name_ingredient = db.Column(
        db.String(128), nullable=False
    )  # Name of the ingredient

    # Relationship with RecipeIngredient model
    recipes = db.relationship("RecipeIngredient", back_populates="ingredient")


class User(UserMixin, db.Model):
    """Represents a user of the application."""

    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)  # Unique username
    email = db.Column(db.String(120), index=True, unique=True)  # Unique email address
    password = db.Column(db.String(255))  # Hashed password for the user
    recipes = db.relationship(
        "Recipe", backref="user", lazy=True
    )  # Recipes created by the user

    # Relationship with Rating model (ratings given by the user)
    ratings = db.relationship("Rating", backref="user", lazy=True)


class Rating(db.Model):
    """Represents a rating given by a user to a recipe."""

    __tablename__ = "rating"
    id = db.Column(db.Integer, primary_key=True)
    stars = db.Column(db.Integer, nullable=False)  # Number of stars (rating)
    recipe_id = db.Column(
        db.Integer, db.ForeignKey("recipe.id"), nullable=False
    )  # Recipe being rated
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )  # User who gave the rating
