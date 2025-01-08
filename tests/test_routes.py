import pytest
from flask import Flask, jsonify, request, url_for
from flask_login import login_user, current_user
from werkzeug.utils import secure_filename
from myflaskapp import create_app
from extensions import db
from models.models_sql import Recipe, User
from services.recipe_service import add_recipe, get_recipe_with_comments, delete_recipe, edit_recipe, rate_recipe
from services.ingredient_service import add_ingredient_to_recipe, delete_ingredient, update_ingredient
from services.comment_service import add_comment, delete_comment, update_comment
from io import BytesIO
import json

# Tests
def test_addrecipe(test_client, user):
    with test_client as c:
        login_user(user)
        response = c.get(url_for('recipes.addrecipe'))
        assert response.status_code == 200
        assert b'Add Recipe' in response.data

def test_addrecipe_with_ingredients(test_client, user):
    with test_client as c:
        login_user(user)
        data = {
            'title': 'Test Recipe',
            'description': 'Test description',
            'ingredients': json.dumps([{'name_ingredient': 'Flour', 'quantity': 2, 'unit': 'cups'}]),
        }
        files = {'recipeImage': (BytesIO(b'test image'), 'test.jpg')}
        response = c.post(url_for('recipes.addrecipe_with_ingredients'), data=data, content_type='multipart/form-data', follow_redirects=True)
        assert response.status_code == 200
        assert 'redirect' in response.json

def test_view_recipe_route(client, user):
    with client as c:
        login_user(user)
        recipe_id = 13  # Assurez-vous que l'ID est correct
        response = c.get(url_for('recipes.view_recipe_route', id=recipe_id))
        assert response.status_code == 200
        assert b'Test Recipe' in response.data

def test_edit_recipe_route(client, user):
    with client as c:
        login_user(user)
        recipe_id = 13  # Assurez-vous que l'ID est correct
        data = {
            'title': 'Updated Recipe Title',
            'description': 'Updated description',
        }
        response = c.post(url_for('recipes.edit_recipe_route', id=recipe_id), data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b'La recette a ete mise a jour avec succes.' in response.data

def test_delete_recipe_route(client, user):
    with client as c:
        login_user(user)
        recipe_id = 13  # Assurez-vous que l'ID est correct
        response = c.post(url_for('recipes.delete_recipe_route', id=recipe_id), follow_redirects=True)
        assert response.status_code == 200
        assert b'La recette a ete supprimee avec succes.' in response.data

def test_add_ingredient_route(client, user):
    with client as c:
        login_user(user)
        recipe_id = 15  # Assurez-vous que l'ID est correct
        data = {
            'name_ingredient': 'Sugar',
            'quantity': '1',
            'unit': 'teaspoon',
        }
        response = c.post(url_for('recipes.add_ingredient_route', recipe_id=recipe_id), data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b'Sugar' in response.data

def test_delete_ingredient_route(client, user):
    with client as c:
        login_user(user)
        recipe_id = 14  # Assurez-vous que l'ID est correct
        ingredient_id = 30  # Assurez-vous que l'ID est correct
        response = c.post(url_for('recipes.delete_ingredient_route', recipe_id=recipe_id, ingredient_id=ingredient_id), follow_redirects=True)
        assert response.status_code == 200
        assert b'Ingredient deleted successfully' in response.data

def test_add_comment_route(client, user):
    with client as c:
        login_user(user)
        recipe_id = 8  # Assurez-vous que l'ID est correct
        data = {'comment': 'This is a test comment'}
        response = c.post(url_for('recipes.add_comment_route', recipe_id=recipe_id), data=data, follow_redirects=True)
        assert response.status_code == 201
        assert b'This is a test comment' in response.data

def test_rate_recipe_route(client, user):
    with client as c:
        login_user(user)
        recipe_id = 15  # Assurez-vous que l'ID est correct
        data = {'stars': 5}
        response = c.post(url_for('recipes.rate_recipe_route', recipe_id=recipe_id), data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b'Rating submitted successfully' in response.data
