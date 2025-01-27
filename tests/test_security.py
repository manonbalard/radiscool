import io
from flask_login import login_user


def test_sql_injection(test_client):
    """Test to check protection against SQL injection."""
    payload = "' OR '1'='1"

    # Perform the POST request with test data
    response = test_client.post(
        "/login", data={"email": payload, "password": "password"}
    )

    # Check that the response is a redirection (status code 302)
    assert response.status_code == 302  # Expected redirection

    # Check that the user is redirected to the login page
    assert response.location.endswith("/login")  # Verifying the relative redirect path


def test_weak_password_rejection(test_client, user):
    """Test pour rejeter les mots de passe faibles."""
    # Effectuer une requête GET pour charger la page de signup
    followup_response = test_client.get("/signup")
    assert followup_response.status_code == 200

    # Effectuer la requête POST avec un mot de passe faible
    response = test_client.post(
        "/signup", data={"email": "test@example.com", "password": "123"}
    )

    # Vérifier que la réponse est une redirection (code HTTP 302)
    assert response.status_code == 302  # Redirection attendue

    # Vérifier que l'utilisateur est redirigé vers la page signup après un échec
    assert response.location.endswith("/signup")  # Redirection vers /signup après échec

    # Vérifier que le message d'erreur "Password is too weak" est dans la réponse
    followup_response = test_client.get("/signup")
    assert (
        b"Password is too weak" in followup_response.data
    )  # Vérifier le message d'erreur


def test_file_upload_restriction_add_recipe(test_client, user):
    """Test to verify that only allowed file types can be uploaded when adding a recipe."""

    # Connecter l'utilisateur et vérifier la session avec test_client
    with test_client:
        # Connexion de l'utilisateur en simulant une requête avec le test client
        login_user(user)
        assert "_user_id" in test_client.session

        # Créer des données de test avec un fichier malveillant
        data = {
            "title": "Test Recipe",
            "description": "A test recipe",
            "ingredients": "[]",  # Exemple d'ingrédient vide
            "recipeImage": (io.BytesIO(b"fake content"), "malicious.exe"),
        }

        # Effectuer un POST vers la route 'addrecipe_with_ingredients'
        response = test_client.post(
            "/addrecipe_with_ingredients", data=data, content_type="multipart/form-data"
        )

        # Vérifier si la réponse contient le message d'erreur concernant le type de fichier
        assert b"File type not allowed" in response.data


def test_error_handling(test_client):
    """Test to ensure that errors do not reveal sensitive information."""
    response = test_client.get("/nonexistent-page")
    assert (
        b"Internal Server Error" not in response.data
    )  # Verify that technical details are not exposed


def test_secure_session_cookie(test_client):
    """Test to check that session cookies are secure."""
    response = test_client.get("/")
    session_cookie = response.headers.get("Set-Cookie")
    assert "HttpOnly" in session_cookie
    assert "Secure" in session_cookie
