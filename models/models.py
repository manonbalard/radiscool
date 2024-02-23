from database import db

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