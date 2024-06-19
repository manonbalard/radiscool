import logging
from flask import render_template, request, redirect, url_for, Blueprint, flash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from models.models  import User

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

    print(email, password, user)

    if not user:
        flash('Please check your login details and try again.')
        return redirect(url_for('users.login')) 

    login_user(user, remember=remember)
    return redirect(url_for('home'))

@users.route('/signup')
def signup():
    return render_template('users/signup.html')

@users.route('/signup', methods=['POST'])
def signup_post():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    if user:
        flash('Email address already exists')
        return redirect(url_for('users.signup'))
    
    new_user = User(email=email, username=username, password=generate_password_hash(password))

    db.session.add(new_user)
    db.session.commit()
    
    return redirect(url_for('users.login'))

@users.route('/profile')
@login_required
def profile():
    return render_template('users/profile.html', name=current_user.username)

@users.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('users.login'))
