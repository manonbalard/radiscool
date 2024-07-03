from flask import current_app, render_template, request, redirect, url_for, Blueprint, flash, jsonify
from flask_login import current_user
from models.models import Ingredient, Recipe
from werkzeug.utils import secure_filename
from extensions import db, photos  # Import photos from extensions
import os, json

recipes = Blueprint('recipes', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@recipes.route("/")
def index():
    all_recipes = Recipe.query.all()
    return render_template('recipes/recipes.html', recipes=all_recipes)

@recipes.route("/addrecipe", methods=['GET'])
def addrecipe():
    return render_template('recipes/add_recipe.html')

@recipes.route('/addrecipe_with_ingredients', methods=['POST'])
def addrecipe_with_ingredients():
    title = request.form['title']
    description = request.form['description']
    ingredients = json.loads(request.form['ingredients'])  # Convert the JSON string back to a Python list

    # Create new_recipe object 
    new_recipe = Recipe(title=title, description=description, user_id=current_user.id)

    # Handling file upload
    if 'recipeImage' in request.files:
        file = request.files['recipeImage']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = photos.save(file, name=filename)
            new_recipe.image = url_for('static', filename='uploads/images/' + filename)

    db.session.add(new_recipe)
    db.session.flush()  

    ingredient_list = ingredients
    for ingredient_data in ingredient_list:
        new_ingredient = Ingredient(
            quantity=ingredient_data['quantity'],
            unit=ingredient_data['unit'],
            name_ingredient=ingredient_data['name'],
            recipe_id=new_recipe.id
        )
        db.session.add(new_ingredient)
    
    db.session.commit()
    return jsonify({'redirect': url_for('recipes.index')})

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
    if request.method == 'POST':
        # Fetch form data
        title = request.form.get('title')
        description = request.form.get('description')
        recipe = Recipe.query.get_or_404(id)
        
        # Update recipe
        recipe.title = title
        recipe.description = description
        
        # Commit changes
        db.session.commit()
        
        # Redirect to a confirmation page or back to the recipe
        return redirect(url_for('recipes.view_recipe', id=id))
    
    # GET request handling (show the form)
    recipe = Recipe.query.get_or_404(id)
    ingredients = recipe.ingredients
    return render_template('recipes/edit_recipe.html', recipe=recipe, ingredients=ingredients)

@recipes.route('/recipes/edit_ingredient/<int:id>', methods=['POST'])
def edit_ingredient(id):
    ingredient = Ingredient.query.get_or_404(id)
    
    # Fetch the JSON data
    data = request.get_json()
    name_ingredient = data.get('name_ingredient')
    quantity = data.get('quantity')
    unit = data.get('unit')

    # Update the ingredient with new values    
    if name_ingredient:
        ingredient.name_ingredient = name_ingredient
    if quantity:
        ingredient.quantity = quantity
    if unit:
        ingredient.unit = unit

    # Commit changes to the database
    db.session.commit()

    # Return the updated ingredient details
    updated_values = {
        'id': ingredient.id,
        'name_ingredient': ingredient.name_ingredient,
        'quantity': ingredient.quantity,
        'unit': ingredient.unit
    }
    return jsonify({'updatedIngredient': updated_values}), 200


@recipes.route('/recipes/add_ingredient/<int:recipe_id>', methods=['POST'])
def add_ingredient(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    
    # Fetch the form data
    name_ingredient = request.form.get('name_ingredient')
    quantity = request.form.get('quantity')
    unit = request.form.get('unit')

    # Create a new ingredient
    new_ingredient = Ingredient(
        name_ingredient=name_ingredient,
        quantity=quantity,
        unit=unit,
        recipe_id=recipe.id
    )

    # Add the new ingredient to the database
    db.session.add(new_ingredient)
    db.session.commit()

    # Return the new ingredient details
    return jsonify({'id': new_ingredient.id, 'name_ingredient': new_ingredient.name_ingredient, 'quantity': new_ingredient.quantity, 'unit': new_ingredient.unit}), 200
