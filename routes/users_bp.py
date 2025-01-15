from flask import render_template, request, redirect, url_for, Blueprint, flash
from flask_login import login_required, current_user, logout_user
from services.user_service import UserService

# Create a blueprint for user-related routes
users = Blueprint("users", __name__)


@users.route("/login")
def login():
    """
    Render the login page.

    Returns:
        Rendered HTML template for the login page.
    """
    return render_template("users/login.html")


@users.route("/login", methods=["POST"])
def login_post():
    """
    Handle user login.

    Retrieves user credentials from the form, authenticates the user,
    and logs them in if successful. Redirects to the next page or home page.

    Returns:
        Redirect to the next page, home page, or login page in case of failure.
    """
    email = request.form.get("email")
    password = request.form.get("password")
    remember = True if request.form.get("remember") else False

    try:
        # Authenticate the user with the provided email and password
        user = UserService.authenticate_user(email, password)
        # Log in the user and set session persistence based on 'remember'
        UserService.login_user(user, remember)

        # Redirect to the page the user originally intended to visit
        next_page = request.args.get("next")
        if next_page:
            return redirect(next_page)
        return redirect(url_for("home"))
    except ValueError as e:
        # Handle authentication failure and display an error message
        flash(str(e))
        return redirect(url_for("users.login"))


@users.route("/signup")
def signup():
    """
    Render the signup page.

    Returns:
        Rendered HTML template for the signup page.
    """
    return render_template("users/signup.html")


@users.route("/signup", methods=["POST"])
def signup_post():
    """
    Handle user signup.

    Creates a new user account based on the form data. Redirects to the login
    page on success or back to the signup page on failure.

    Returns:
        Redirect to the login page or signup page in case of failure.
    """
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    try:
        # Create a new user in the database
        UserService.create_user(username, email, password)
        flash("Registration successful", "success")
        return redirect(url_for("users.login"))
    except ValueError as e:
        # Handle registration failure and display an error message
        flash(str(e), "error")
        return redirect(url_for("users.signup"))


@users.route("/profile")
@login_required
def profile():
    """
    Display the user's profile page.

    Returns:
        Rendered HTML template for the profile page with user information.
    """
    return render_template("users/profile.html", name=current_user.username)


@users.route("/logout")
@login_required
def logout():
    """
    Log out the current user and redirect to the login page.

    Returns:
        Redirect to the login page.
    """
    # Log out the user using the service function
    UserService.logout_user(logout_user)
    return redirect(url_for("users.login"))
