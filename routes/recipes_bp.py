from flask import current_app, render_template, request, redirect, url_for, Blueprint, flash, jsonify
from flask_login import login_required, current_user
from models.models_sql import Ingredient, Recipe, RecipeIngredient
from models.models_nosql import CommentNoSQL
from werkzeug.utils import secure_filename
from extensions import db, photos  
import os, json

recipes = Blueprint('recipes', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@recipes.route("/")
def index():
    all_recipes = Recipe.query.all()
    return render_template('recipes/recipes.html', recipes=all_recipes)

@recipes.route('/addrecipe', methods=['GET'])
def addrecipe():
    return render_template('recipes/add_recipe.html')

@recipes.route('/addrecipe_with_ingredients', methods=['POST'])
@login_required
def addrecipe_with_ingredients():
    title = request.form['title']
    description = request.form['description']
    ingredients = json.loads(request.form['ingredients'])  # Convertir la chaîne JSON en liste Python

    # Créer un objet Recipe
    new_recipe = Recipe(title=title, description=description, user_id=current_user.id)

    # Gestion du téléchargement de fichier
    if 'recipeImage' in request.files:
        file = request.files['recipeImage']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = photos.save(file, name=filename)
            new_recipe.image = 'uploads/images/' + filename

    # Ajouter la recette à la session
    db.session.add(new_recipe)
    db.session.flush()  # Flush pour obtenir l'ID de la recette

    # Ajouter les ingrédients via la table intermédiaire
    for ingredient_data in ingredients:
        ingredient_name = ingredient_data['name']
        ingredient = Ingredient.query.filter_by(name_ingredient=ingredient_name).first()

        if not ingredient:
            # Si l'ingrédient n'existe pas, on le crée
            ingredient = Ingredient(name_ingredient=ingredient_name)
            db.session.add(ingredient)
            db.session.flush()  # Flush pour obtenir l'ID de l'ingrédient

        # Ajouter la relation entre recette et ingrédient dans la table RecipeIngredient
        new_recipe_ingredient = RecipeIngredient(
            recipe_id=new_recipe.id,
            ingredient_id=ingredient.id,
            quantity=ingredient_data['quantity'],
            unit=ingredient_data['unit']
        )
        db.session.add(new_recipe_ingredient)

    db.session.commit()

    return jsonify({'redirect': url_for('recipes.view_recipe', id=new_recipe.id)})


@recipes.route('/<int:id>')
def view_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    return render_template('recipes/view_recipe.html', recipe=recipe)

@recipes.route('/delete/<int:id>', methods=['POST'])
def delete_recipe(id):
    recipe = Recipe.query.get_or_404(id)

    # Supprimer les entrées dans la table intermédiaire RecipeIngredient
    RecipeIngredient.query.filter_by(recipe_id=recipe.id).delete()

    # Supprimer la recette
    db.session.delete(recipe)
    db.session.commit()

    flash('Recipe deleted.')
    return redirect(url_for('recipes.index'))

@recipes.route('/delete_ingredient/<int:recipe_id>/<int:ingredient_id>', methods=['POST'])
def delete_ingredient(recipe_id, ingredient_id):
    # Trouve la relation entre la recette et l'ingrédient dans RecipeIngredient
    recipe_ingredient = RecipeIngredient.query.filter_by(recipe_id=recipe_id, ingredient_id=ingredient_id).first_or_404()

    # Supprime la relation
    db.session.delete(recipe_ingredient)
    db.session.commit()

    return jsonify({'message': 'Ingrédient supprimé avec succès'}), 200


@recipes.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_recipe(id):
    recipe = Recipe.query.get_or_404(id)

    if request.method == 'POST':
        # Mise à jour des informations de la recette
        title = request.form.get('title')
        description = request.form.get('description')
        ingredients = request.form.get('ingredients', None)

        # Convertir JSON string to list si des ingrédients sont fournis
        if ingredients is not None:
            ingredients = json.loads(ingredients)  # Convert JSON string to list
        else:
            ingredients = []  # Initialise comme une liste vide si pas d'ingrédients fournis

        # Vérifier les ingrédients existants
        existing_ingredients = RecipeIngredient.query.filter_by(recipe_id=recipe.id).all()

        # Si aucune nouvelle liste d'ingrédients n'est fournie, on renvoie une erreur
        if not ingredients and not existing_ingredients:
            return "At least one ingredient is required", 400

        # Mise à jour des informations de la recette
        recipe.title = title
        recipe.description = description

        # Supprimer les relations existantes pour cette recette uniquement si de nouveaux ingrédients sont fournis
        if ingredients:
            RecipeIngredient.query.filter_by(recipe_id=recipe.id).delete()

            # Ajouter de nouvelles relations avec les ingrédients
            for ingredient_data in ingredients:
                ingredient_name = ingredient_data['name']
                ingredient = Ingredient.query.filter_by(name_ingredient=ingredient_name).first()
                if not ingredient:
                    # Si l'ingrédient n'existe pas, on le crée
                    ingredient = Ingredient(name_ingredient=ingredient_name)
                    db.session.add(ingredient)
                    db.session.flush()

                new_recipe_ingredient = RecipeIngredient(
                    recipe_id=recipe.id,
                    ingredient_id=ingredient.id,
                    quantity=ingredient_data['quantity'],
                    unit=ingredient_data['unit']
                )
                db.session.add(new_recipe_ingredient)

        db.session.commit()
        return redirect(url_for('recipes.view_recipe', id=id))

    # Récupérer les ingrédients avec leurs IDs
    ingredients = RecipeIngredient.query.filter_by(recipe_id=recipe.id).all()
    return render_template('recipes/edit_recipe.html', recipe=recipe, ingredients=ingredients)

@recipes.route('/edit_ingredient/<int:recipe_id>/<int:ingredient_id>', methods=['POST'])
def edit_ingredient(recipe_id, ingredient_id):
    # Récupérer la relation RecipeIngredient existante
    recipe_ingredient = RecipeIngredient.query.filter_by(recipe_id=recipe_id, ingredient_id=ingredient_id).first()
    if recipe_ingredient is None:
        print(f"RecipeIngredient not found for recipe_id={recipe_id} and ingredient_id={ingredient_id}")
        return jsonify({'message': 'Ingredient not found'}), 404

    # Récupérer les nouvelles données du formulaire ou de la requête JSON
    data = request.get_json()
    quantity = data.get('quantity')
    unit = data.get('unit')

    # Mise à jour des quantités et unités si disponibles
    if quantity is not None:
        recipe_ingredient.quantity = quantity
    if unit is not None:
        recipe_ingredient.unit = unit

    db.session.commit()

    return jsonify({'message': 'Ingredient updated successfully'}), 200



@recipes.route('/add_ingredient/<int:recipe_id>', methods=['POST'])
def add_ingredient(recipe_id):
    try:
        recipe = Recipe.query.get_or_404(recipe_id)

        # Récupérer les données du formulaire
        name_ingredient = request.form.get('name_ingredient')
        quantity = request.form.get('quantity')
        unit = request.form.get('unit')

        # Validation des données
        if not name_ingredient or not quantity or not unit:
            return jsonify({'error': 'All fields are required'}), 400

        # Trouver ou créer l'ingrédient
        ingredient = Ingredient.query.filter_by(name_ingredient=name_ingredient).first()
        if not ingredient:
            ingredient = Ingredient(name_ingredient=name_ingredient)
            db.session.add(ingredient)
            db.session.flush()

        # Vérifier si la relation existe déjà dans RecipeIngredient
        existing_recipe_ingredient = RecipeIngredient.query.filter_by(
            recipe_id=recipe.id,
            ingredient_id=ingredient.id
        ).first()

        if existing_recipe_ingredient:
            # Si la relation existe, mettez à jour la quantité et l'unité
            existing_recipe_ingredient.quantity = float(quantity)
            existing_recipe_ingredient.unit = unit
        else:
            # Si la relation n'existe pas, créez-la
            new_recipe_ingredient = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ingredient.id,
                quantity=float(quantity),
                unit=unit
            )
            db.session.add(new_recipe_ingredient)

        db.session.commit()

        return jsonify({
                'id': ingredient.id,
                'name_ingredient': ingredient.name_ingredient,
                'quantity': quantity,
                'unit': unit,
                'message': 'Ingrédient ajouté avec succès !'
            }), 200
    except Exception as e:
        print("Error:", str(e))  # Log the error message
        return jsonify({'error': 'An error occurred'}), 500


@recipes.route('/<int:recipe_id>/add_comment', methods=['POST'])
def add_comment(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    text = request.form.get('comment')
    
    if not text:
        return jsonify({"error": "Comment cannot be empty"}), 400

    # Créer un nouveau commentaire et le sauvegarder dans MongoDB
    new_comment = CommentNoSQL(recipe_id=recipe.id, user_id=current_user.id, text=text)
    new_comment.save()
    
    return jsonify({"message": "Comment added"}), 201

@recipes.route('/<int:recipe_id>/comments', methods=['GET'])
def get_comments(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    
    # Récupérer les commentaires depuis MongoDB
    comments = CommentNoSQL.get_comments_by_recipe(recipe_id)
    
    comments_data = []
    for comment in comments:
        comments_data.append({
            "user_id": comment['user_id'],
            "text": comment['text'],
            "date": comment['date']
        })
    
    return jsonify(comments_data), 200

@recipes.route('/comments/delete/<comment_id>', methods=['POST'])
def delete_comment(comment_id):
    result = CommentNoSQL.delete_comment(comment_id)
    
    if result.deleted_count == 1:
        return jsonify({"message": "Comment deleted"}), 200
    else:
        return jsonify({"error": "Comment not found"}), 404


@recipes.route('/comments/edit/<comment_id>', methods=['POST'])
def edit_comment(comment_id):
    new_text = request.form.get('comment')
    
    if not new_text:
        return jsonify({"error": "Comment cannot be empty"}), 400

    result = CommentNoSQL.update_comment(comment_id, new_text)
    
    if result.modified_count == 1:
        return jsonify({"message": "Comment updated"}), 200
    else:
        return jsonify({"error": "Comment not found"}), 404
    

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
