from flask import current_app, render_template, request, redirect, url_for, Blueprint, flash, jsonify
from flask_login import current_user
from models.models import Ingredient, Recipe, recipe_ingredient
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

    # Créer un objet Recipe
    new_recipe = Recipe(title=title, description=description, user_id=current_user.id)

    # Gestion du téléchargement de fichier
    if 'recipeImage' in request.files:
        file = request.files['recipeImage']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = photos.save(file, name=filename)
            new_recipe.image = url_for('static', filename='uploads/images/' + filename)

    # Ajouter la recette à la session
    db.session.add(new_recipe)
    db.session.flush()  # Pour obtenir l'ID de la recette avant l'insertion des ingrédients

    # Ajouter les ingrédients via la table intermédiaire
    for ingredient_data in ingredients:
        ingredient_name = ingredient_data['name']
        ingredient = Ingredient.query.filter_by(name_ingredient=ingredient_name).first()
        if not ingredient:
            # Si l'ingrédient n'existe pas, on le crée
            ingredient = Ingredient(name_ingredient=ingredient_name)
            db.session.add(ingredient)

        # Ajout de la relation dans la table intermédiaire
        db.session.execute(recipe_ingredient.insert().values(
            recipe_id=new_recipe.id,
            ingredient_id=ingredient.id,
            quantity=ingredient_data['quantity'],
            unit=ingredient_data['unit']
        ))

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

    # Supprimer les entrées dans la table intermédiaire
    db.session.execute(recipe_ingredient.delete().where(recipe_ingredient.c.recipe_id == id))

    # Supprimer la recette
    db.session.delete(recipe)
    db.session.commit()
    
    flash('Recipe deleted.')
    return redirect(url_for('recipes.index'))


@recipes.route('/recipes/edit/<int:id>', methods=['GET', 'POST'])
def edit_recipe(id):
    recipe = Recipe.query.get_or_404(id)

    if request.method == 'POST':
        # Mise à jour des informations de la recette
        title = request.form.get('title')
        description = request.form.get('description')
        ingredients = json.loads(request.form['ingredients'])  # Convert JSON string to list

        recipe.title = title
        recipe.description = description

        # Suppression des relations existantes pour cette recette
        db.session.execute(recipe_ingredient.delete().where(recipe_ingredient.c.recipe_id == id))

        # Ajouter de nouvelles relations avec les ingrédients
        for ingredient_data in ingredients:
            ingredient_name = ingredient_data['name']
            ingredient = Ingredient.query.filter_by(name_ingredient=ingredient_name).first()
            if not ingredient:
                # Si l'ingrédient n'existe pas, on le crée
                ingredient = Ingredient(name_ingredient=ingredient_name)
                db.session.add(ingredient)

            # Ajouter la relation dans la table intermédiaire
            db.session.execute(recipe_ingredient.insert().values(
                recipe_id=recipe.id,
                ingredient_id=ingredient.id,
                quantity=ingredient_data['quantity'],
                unit=ingredient_data['unit']
            ))

        db.session.commit()
        return redirect(url_for('recipes.view_recipe', id=id))

    ingredients = recipe.ingredients
    return render_template('recipes/edit_recipe.html', recipe=recipe, ingredients=ingredients)


@recipes.route('/recipes/edit_ingredient/<int:id>', methods=['POST'])
def edit_ingredient(id):
    ingredient = Ingredient.query.get_or_404(id)
    
    # Debug: Print request data
    print("Request Data:", request.data)
    print("Request JSON:", request.json)

    # Fetch the JSON data
    data = request.get_json()
    print("Received JSON Data:", data)

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
    
    # Récupérer les données du formulaire
    name_ingredient = request.form.get('name_ingredient')
    quantity = request.form.get('quantity')
    unit = request.form.get('unit')

    # Trouver ou créer l'ingrédient
    ingredient = Ingredient.query.filter_by(name_ingredient=name_ingredient).first()
    if not ingredient:
        ingredient = Ingredient(name_ingredient=name_ingredient)
        db.session.add(ingredient)
        db.session.flush()

    # Ajouter la relation dans la table intermédiaire
    db.session.execute(recipe_ingredient.insert().values(
        recipe_id=recipe.id,
        ingredient_id=ingredient.id,
        quantity=quantity,
        unit=unit
    ))

    db.session.commit()

    # Retourner les détails du nouvel ingrédient
    return jsonify({'id': ingredient.id, 'name_ingredient': ingredient.name_ingredient, 'quantity': quantity, 'unit': unit}), 200
