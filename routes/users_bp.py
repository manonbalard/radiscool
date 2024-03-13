from flask import render_template, request, redirect, url_for, Blueprint, flash, jsonify
from flask_login import login_user
from database import db
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

    if not user or not check_password_hash(user.password, password):
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
def profile():
    return render_template('users/profile.html')