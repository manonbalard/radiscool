from flask import render_template, request, redirect, url_for, Blueprint, flash, jsonify
from database import db
from models.models  import Ingredient, Recipe

recipes = Blueprint('recipes', __name__)

@recipes.route("/")
def index():
    all_recipes = Recipe.query.all()
    return render_template('recipes/recipes.html', recipes = all_recipes)

@recipes.route("/addrecipe", methods=['GET'])
def addrecipe():
    return render_template('recipes/add_recipe.html')

@recipes.route('/addrecipe_with_ingredients', methods=['POST'])
def addrecipe_with_ingredients():
    data = request.json
    title = data.get('title')
    description = data.get('description')
    ingredient_list = data.get('ingredients', [])

    new_recipe = Recipe(title=title, description=description)
    db.session.add(new_recipe)
    db.session.flush()  

    for ingredient_data in ingredient_list:
        new_ingredient = Ingredient(
            quantity=ingredient_data['quantity'],
            unit=ingredient_data['unit'],
            name_ingredient=ingredient_data['name'],
            recipe_id=new_recipe.id
        )
        db.session.add(new_ingredient)
    
    db.session.commit()

    return jsonify({'success': True, 'recipe_id': new_recipe.id})

@recipes.route('/recipes/<int:id>')
def view_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    ingredients = recipe.ingredients
    return render_template('recipes/view_recipe.html', recipe=recipe, ingredients=ingredients)

@recipes.route('/recipes/delete/<int:id>', methods=['POST'])
def delete_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    Ingredient.query.filter_by(recipe_id=id).delete()
    db.session.delete(recipe)
    db.session.commit()
    flash('Recipe deleted.')
    return redirect(url_for('recipes.index'))

@recipes.route('/recipes/edit/<int:id>', methods=['GET', 'POST'])
def edit_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    return render_template('recipes/edit_recipe.html', recipe=recipe)