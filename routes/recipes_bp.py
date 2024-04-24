from flask import current_app, render_template, request, redirect, url_for, Blueprint, flash, jsonify
from database import db
from models.models  import Ingredient, Recipe
from werkzeug.utils import secure_filename
import os, json

recipes = Blueprint('recipes', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@recipes.route("/")
def index():
    all_recipes = Recipe.query.all()
    return render_template('recipes/recipes.html', recipes = all_recipes)

@recipes.route("/addrecipe", methods=['GET'])
def addrecipe():
    return render_template('recipes/add_recipe.html')

@recipes.route('/addrecipe_with_ingredients', methods=['POST'])
def addrecipe_with_ingredients():
    title = request.form['title']
    description = request.form['description']
    ingredients = json.loads(request.form['ingredients'])  # Convert the JSON string back to a Python list

    # Create new_recipe object from the Recipe model first
    new_recipe = Recipe(title=title, description=description)

     # Handling file upload
    file = request.files['recipeImage']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        # Assuming you have an image field in your Recipe model
        new_recipe.image = url_for('static', filename='uploads/' + filename)

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
    return render_template('recipes/edit_recipe.html', recipe=recipe)

@recipes.route('recipes/edit_ingredient/<int:id>', methods=['POST'])
def edit_ingredient(id):
    ingredient = Ingredient.query.get_or_404(id)
    
    # Fetch the form data
    name_ingredient = request.form.get('name_ingredient')
    quantity = request.form.get('quantity')
    unit = request.form.get('unit')

    # Update the ingredient with new values    
    updated_values = {}
    if name_ingredient:
        ingredient.name_ingredient = name_ingredient
        updated_values['name_ingredient'] = name_ingredient
    if quantity:
        ingredient.quantity = quantity
        updated_values['quantity'] = quantity
    if unit:
        ingredient.unit = unit
        updated_values['unit'] = unit

    # Commit changes to the database
    db.session.commit()

    # Return the updated ingredient details
    updated_values['id'] = ingredient.id  # Make sure to return the id for client-side use
    return jsonify({'updatedIngredient': updated_values}), 200
