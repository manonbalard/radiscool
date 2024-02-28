from flask import render_template, request, redirect, url_for, Blueprint, flash, jsonify
from database import db
from models.models  import User

users = Blueprint('users', __name__)

@users.route('/login')
def login():
    return render_template('login.html')

@users.route('/signup')
def login():
    return render_template('signup.html')

@users.route('/profile')
def login():
    return render_template('profile.html')