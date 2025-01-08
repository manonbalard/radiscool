import logging
from flask import render_template, request, redirect, url_for, Blueprint, flash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from models.models_sql  import User
import re

users = Blueprint('users', __name__)

@users.route('/login')
def login():
    return render_template('users/login.html')

@users.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    if not user:
        flash('Email not found.')
        print("Utilisateur introuvable pour l'email :", email)
        return redirect(url_for('users.login'))

    if not check_password_hash(user.password, password):
        flash('Password incorrect.')
        print("Mot de passe incorrect pour l'utilisateur :", user.email)
        return redirect(url_for('users.login'))

    login_user(user, remember=remember)

    next_page = request.args.get('next')
    if next_page:
        return redirect(next_page)  # Redirige vers l'URL initiale après la connexion
    return redirect(url_for('home'))  # Sinon, redirige vers la page d'accueil

@users.route('/signup')
def signup():
    return render_template('users/signup.html')

@users.route('/signup', methods=['POST'])
def signup_post():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    # Vérification de la force du mot de passe
    if len(password) < 6:
        flash('Password is too weak')  # Message d'erreur si le mot de passe est trop faible
        return redirect(url_for('users.signup'))  # Redirection vers la page d'inscription si le mot de passe est faible

    # Vérifiez si l'utilisateur existe déjà
    user = User.query.filter_by(email=email).first()
    if user:
        flash('Email address already exists')
        return redirect(url_for('users.signup'))
    
    # Hachage du mot de passe
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

    # Création du nouvel utilisateur
    new_user = User(email=email, username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    
    # Redirige l'utilisateur vers la page de connexion
    return redirect(url_for('users.login'))  # Redirection vers la page de connexion après une inscription réussie


@users.route('/profile')
@login_required
def profile():
    return render_template('users/profile.html', name=current_user.username)

@users.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('users.login'))
