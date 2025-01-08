from flask import current_app
from models.models_sql import Recipe, RecipeIngredient, Ingredient, Rating
from extensions import db, photos 
import json
import imghdr
from werkzeug.utils import secure_filename

def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def validate_image(file):
    """Valide si le fichier est réellement une image en vérifiant son type MIME."""
    if not file:
        return False
    file_type = imghdr.what(file)
    return file_type in current_app.config['ALLOWED_EXTENSIONS']

def validate_recipe_data(title, description, ingredients_json):
    errors = {}
    if not title or len(title) < 3:
        errors['title'] = 'Le titre doit comporter au moins 3 caractères.'
    if not isinstance(ingredients_json, str):
        errors['ingredients_json'] = 'Les ingrédients doivent être une chaîne JSON valide.'
    return errors


def add_recipe(title, description, ingredients_json, user_id, image_file):
    try:
        # Validation des données
        errors = validate_recipe_data(title, description, ingredients_json)
        if errors:
            return {'error': True, 'message': errors}

        # Traitement normal après validation
        ingredients = json.loads(ingredients_json)
        new_recipe = Recipe(title=title, description=description, user_id=user_id)

        # Gestion de l'image
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            file_path = photos.save(image_file, name=filename)
            new_recipe.image = 'uploads/images/' + filename

        db.session.add(new_recipe)
        db.session.flush()

        for ingredient_data in ingredients:
            ingredient_name = ingredient_data['name']
            ingredient = Ingredient.query.filter_by(name_ingredient=ingredient_name).first()
            if not ingredient:
                ingredient = Ingredient(name_ingredient=ingredient_name)
                db.session.add(ingredient)
                db.session.flush()

            new_recipe_ingredient = RecipeIngredient(
                recipe_id=new_recipe.id,
                ingredient_id=ingredient.id,
                quantity=ingredient_data['quantity'],
                unit=ingredient_data['unit']
            )
            db.session.add(new_recipe_ingredient)

        db.session.commit()
        return {'error': False, 'recipe_id': new_recipe.id}
    
    except Exception as e:
        db.session.rollback()
        return {'error': True, 'message': str(e)}


def get_recipe_with_comments(id):
    try:
        recipe = Recipe.query.get_or_404(id)
        comments = recipe.get_comments()
        return {'error': False, 'recipe': recipe, 'comments': comments}
    
    except Exception as e:
        return {'error': True, 'message': str(e)}

def validate_id(id_value, id_name="ID"):
    if not isinstance(id_value, int) or id_value <= 0:
        return f"{id_name} doit être un entier positif."
    return None


def delete_recipe(id):
    try:
        error = validate_id(id, "Recipe ID")
        if error:
            return {'error': True, 'message': error}
        # Récupérer la recette à supprimer
        recipe = Recipe.query.get_or_404(id)
        
        # Récupérer les ingrédients liés à cette recette
        recipe_ingredients = RecipeIngredient.query.filter_by(recipe_id=recipe.id).all()

        # Supprimer les relations de RecipeIngredient
        RecipeIngredient.query.filter_by(recipe_id=recipe.id).delete()

        # Pour chaque ingrédient, vérifier s'il est utilisé dans une autre recette
        for relation in recipe_ingredients:
            ingredient_id = relation.ingredient_id
            
            # Vérifier si l'ingrédient est utilisé ailleurs
            other_relations = RecipeIngredient.query.filter_by(ingredient_id=ingredient_id).count()
            if other_relations == 0:
                # Supprimer l'ingrédient s'il n'est pas utilisé dans d'autres recettes
                Ingredient.query.filter_by(id=ingredient_id).delete()
        
        # Supprimer la recette
        db.session.delete(recipe)
        db.session.commit()
        
        return {'error': False, 'message': 'Recipe and unused ingredients deleted.'}
    
    except Exception as e:
        db.session.rollback()  # Revenir en arrière en cas d'erreur
        return {'error': True, 'message': str(e)}


def edit_recipe(id, title, description, ingredients_json, image_file=None):
    try:
        recipe = Recipe.query.get_or_404(id)
        
        # Mise à jour des informations de la recette
        recipe.title = title
        recipe.description = description

        # Gestion de l'image
        if image_file and allowed_file(image_file.filename):
            # Sécurisation du nom du fichier
            filename = secure_filename(image_file.filename)
            filepath = photos.save(image_file, name=filename)
                        
            # Mise à jour du chemin de l'image dans la base de données
            recipe.image = 'uploads/images/' + filename
            
        # Gestion des ingrédients
        ingredients = json.loads(ingredients_json)
        RecipeIngredient.query.filter_by(recipe_id=recipe.id).delete()

        for ingredient_data in ingredients:
            ingredient_name = ingredient_data['name']
            ingredient = Ingredient.query.filter_by(name_ingredient=ingredient_name).first()

            if not ingredient:
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
        return {'error': False, 'message': 'Recipe updated successfully.'}
    
    except Exception as e:
        return {'error': True, 'message': str(e)}

def rate_recipe(recipe_id, user_id, stars):
    """
    Service pour ajouter ou mettre à jour une note pour une recette.
    
    Args:
        recipe_id (int): ID de la recette.
        user_id (int): ID de l'utilisateur qui note.
        stars (int): Note attribuée (1 à 5).
    
    Returns:
        dict: Résultat de l'opération avec un message.
    """
    try:
        if stars < 1 or stars > 5:
            return {'error': True, 'message': 'La note doit être comprise entre 1 et 5.'}

        # Vérifier si une note existe déjà pour cet utilisateur et cette recette
        existing_rating = Rating.query.filter_by(recipe_id=recipe_id, user_id=user_id).first()
        if existing_rating:
            existing_rating.stars = stars
            message = 'Votre note a été mise à jour.'
        else:
            # Créer une nouvelle note si elle n'existe pas
            new_rating = Rating(stars=stars, recipe_id=recipe_id, user_id=user_id)
            db.session.add(new_rating)
            message = 'Votre note a été ajoutée.'

        db.session.commit()
        return {'error': False, 'message': message}
    
    except Exception as e:
        db.session.rollback()  # Annuler la transaction en cas d'erreur
        return {'error': True, 'message': str(e)}


