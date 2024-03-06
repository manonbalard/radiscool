from flask import render_template, request, redirect, url_for, Blueprint, flash, jsonify
from database import db
from models.models  import User

users = Blueprint('users', __name__)

@users.route('/login')
def login():
    return render_template('users/login.html')

@users.route('/signup')
def signup():
    return render_template('users/signup.html')

@users.route('/profile')
def profile():
    return render_template('users/profile.html')