from flask import current_app, render_template, request, redirect, url_for, flash, jsonify, Blueprint
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models.models_sql import Ingredient, Recipe, RecipeIngredient, User, Rating
from models.models_nosql import CommentNoSQL
from services.recipe_service import add_recipe, get_recipe_with_comments, delete_recipe, edit_recipe, allowed_file, validate_image, rate_recipe
from services.ingredient_service import add_ingredient_to_recipe, delete_ingredient, update_ingredient
from services.comment_service import add_comment, delete_comment, update_comment
from extensions import photos
import os, json


recipes = Blueprint('recipes', __name__)

@recipes.route('/addrecipe', methods=['GET'])
def addrecipe():
    return render_template('recipes/add_recipe.html')

@recipes.route('/addrecipe_with_ingredients', methods=['POST'])
@login_required
def addrecipe_with_ingredients():
    title = request.form['title']
    description = request.form['description']
    ingredients = request.form['ingredients']  # JSON string
    
    # Appel au service pour ajouter une recette
    result = add_recipe(title, description, ingredients, current_user.id, request.files.get('recipeImage'))
    
    if result['error']:
        flash(result['message'], 'danger')
        return redirect(url_for('recipes.addrecipe'))

    return jsonify({'redirect': url_for('recipes.view_recipe', id=result['recipe_id'])})


@recipes.route('/recipes/<int:id>', methods=['GET'])
def view_recipe_route(id):
    # Appel au service pour obtenir la recette et les commentaires
    result = get_recipe_with_comments(id)
    
    if result['error']:
        flash(result['message'], 'danger')
        return redirect(url_for('recipes.index'))
    
    return render_template('recipes/view_recipe.html', recipe=result['recipe'], comments=result['comments'])

@recipes.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_recipe_route(id):
    result = delete_recipe(id)
    
    if result['error']:
        flash(result['message'], 'danger')
    else:
        flash(result['message'], 'success')
    
    return redirect(url_for('recipes.index'))

@recipes.route('/delete_ingredient/<int:recipe_id>/<int:ingredient_id>', methods=['POST'])
@login_required
def delete_ingredient_route(recipe_id, ingredient_id):
    result = delete_ingredient(recipe_id, ingredient_id)
    
    return jsonify({'message': result['message']}), 200 if not result['error'] else 400

@recipes.route('/edit_recipe/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_recipe_route(id):
    if request.method == 'POST':
        # Récupération des données du formulaire
        title = request.form['title']
        description = request.form['description']
        ingredients = request.form.get('ingredients', '[]')  # Valeur par défaut si aucun ingrédient
        image_file = request.files.get('recipeImage')  # Récupérer l'image si elle existe
        
        # Appel au service pour éditer la recette
        result = edit_recipe(id, title, description, ingredients, image_file)
        
        if result['error']:
            flash(result['message'], 'danger')
            return redirect(url_for('recipes.edit_recipe_route', id=id))
        
        flash('La recette a été mise à jour avec succès.', 'success')
        return redirect(url_for('recipes.view_recipe_route', id=id))
    
    # Route GET : afficher la recette à éditer
    recipe = Recipe.query.get(id)  # Récupère la recette depuis la base de données
    if not recipe:
        flash("La recette demandée est introuvable.", "danger")
        return redirect(url_for('recipes.list_recipes'))  # Redirige vers une liste ou une autre page appropriée
    
    ingredients = RecipeIngredient.query.filter_by(recipe_id=recipe.id).all()
    return render_template('recipes/edit_recipe.html', recipe=recipe, ingredients=ingredients)



@recipes.route('/edit_ingredient/<int:recipe_id>/<int:ingredient_id>', methods=['POST'])
@login_required
def edit_ingredient_route(recipe_id, ingredient_id):
    data = request.get_json()
    quantity = data.get('quantity')
    unit = data.get('unit')

    result = update_ingredient(recipe_id, ingredient_id, quantity, unit)
    
    return jsonify({'message': result['message']}), 200 if not result['error'] else 400

@recipes.route('/add_ingredient/<int:recipe_id>', methods=['POST'])
@login_required
def add_ingredient_route(recipe_id):
    name_ingredient = request.form.get('name_ingredient')
    quantity = request.form.get('quantity')
    unit = request.form.get('unit')

    # Appel au service pour ajouter un ingrédient
    result = add_ingredient_to_recipe(recipe_id, name_ingredient, quantity, unit)

    if result['error']:
        return jsonify({'error': result['message']}), 400
    return jsonify({
        'id': result['ingredient_id'],
        'name_ingredient': name_ingredient,
        'quantity': quantity,
        'unit': unit,
        'message': result['message']
    }), 200

@recipes.route('/get_ingredients/<int:recipe_id>', methods=['GET'])
def get_ingredients(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    ingredients = [{
        'id': ri.ingredient.id,
        'name': ri.ingredient.name_ingredient,
        'quantity': ri.quantity,
        'unit': ri.unit
    } for ri in recipe.ingredients]

    return jsonify(ingredients), 200

@recipes.route("/")
def index():
    all_recipes = Recipe.query.all()

    # Récupérer les évaluations et calculer la moyenne des notes pour chaque recette
    recipes_with_comments_and_ratings = [
        {
            "id": recipe.id,
            "title": recipe.title,
            "image": recipe.image,
            "average_rating": recipe.average_rating,  # Inclure la moyenne des notes
            "comments": recipe.get_comments(),
        }
        for recipe in all_recipes
    ]

    return render_template('recipes/recipes.html', recipes=recipes_with_comments_and_ratings)


@recipes.route('/<int:recipe_id>/add_comment', methods=['POST'])
@login_required
def add_comment_route(recipe_id):
    text = request.form.get('comment')

    if not text:
        return jsonify({"error": "Comment cannot be empty"}), 400

    # Appel au service pour ajouter un commentaire
    result = add_comment(recipe_id, current_user.id, text)

    if result['error']:
        return jsonify({"error": result['message']}), 400
    return jsonify({"message": result['message']}), 201

@recipes.route('/comments/delete/<comment_id>', methods=['POST'])
@login_required
def delete_comment_route(comment_id):
    result = delete_comment(comment_id)

    if result['error']:
        return jsonify({"error": result['message']}), 400
    return jsonify({"message": result['message']}), 200

@recipes.route('/comments/edit/<comment_id>', methods=['POST'])
@login_required
def edit_comment_route(comment_id):
    new_text = request.form.get('comment')

    if not new_text:
        return jsonify({"error": "Comment cannot be empty"}), 400

    # Appel au service pour éditer un commentaire
    result = update_comment(comment_id, new_text)

    if result['error']:
        return jsonify({"error": result['message']}), 400
    return jsonify({"message": result['message']}), 200

@recipes.route('/recipes/rate/<int:recipe_id>', methods=['POST'])
@login_required
def rate_recipe_route(recipe_id):
    try:
        stars = int(request.form.get('stars'))
        result = rate_recipe(recipe_id=recipe_id, user_id=current_user.id, stars=stars)
        
        if result['error']:
            flash(result['message'], 'danger')
        else:
            flash(result['message'], 'success')
    
    except ValueError:
        flash('Valeur incorrecte pour la note.', 'danger')

    return redirect(url_for('recipes.index'))
