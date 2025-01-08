import pytest
import io
from flask import  url_for

def test_sql_injection(test_client):
    """Test pour vérifier la protection contre l'injection SQL."""
    payload = "' OR '1'='1"

    # Effectuer la requête POST avec les données de test
    response = test_client.post('/login', data={'email': payload, 'password': 'password'})

    # Vérifiez que la réponse est une redirection (code 302)
    assert response.status_code == 302  # Redirection attendue

    # Vérifiez que l'utilisateur est redirigé vers la page de connexion
    assert response.location.endswith('/login')  # Vérification du chemin de redirection relatif

def test_weak_password_rejection(test_client):
    """Test pour refuser les mots de passe faibles."""
    with test_client.application.app_context():
        followup_response = test_client.get('/signup')
        assert followup_response.status_code == 200

    # Effectuer la requête POST avec un mot de passe faible
    response = test_client.post('/signup', data={'email': 'test@example.com', 'password': '123'})

    # Vérifiez que la réponse est une redirection (code 302)
    assert response.status_code == 302  # Redirection attendue

    # Vérifiez que l'utilisateur est redirigé vers la page d'inscription après une inscription échouée
    assert response.location.endswith('/signup')  # Redirection vers la page d'inscription après l'échec de l'inscription

    # Vérifiez que le message d'erreur "Password is too weak" est dans la réponse
    followup_response = test_client.get('/signup')
    assert b"Password is too weak" in followup_response.data  # Vérifiez que le message d'erreur est bien présent


def test_xss_protection(test_client):
    """Test pour vérifier la protection contre les attaques XSS."""
    payload = "<script>alert('XSS')</script>"
    response = test_client.post('/comments', data={'content': payload})
    assert payload.encode() not in response.data  # S'assurer que le script n'est pas rendu tel quel


def test_csrf_protection(test_client):
    """Test pour vérifier la protection CSRF."""
    response = test_client.post('/profile/update', data={'email': 'new@example.com'})
    assert response.status_code == 400  # Une requête sans jeton CSRF valide doit échouer


def test_access_restriction(test_client):
    """Test pour s'assurer que les utilisateurs non connectés ne peuvent pas accéder aux pages restreintes."""
    response = test_client.get('/admin')
    assert response.status_code == 403  # Vérifier que l'accès est refusé pour les utilisateurs non autorisés


def test_file_upload_restriction(test_client):
    """Test pour vérifier que seuls les fichiers autorisés peuvent être téléchargés."""
    data = {
        'file': (io.BytesIO(b"fake content"), 'malicious.exe')
    }
    response = test_client.post('/upload', data=data, content_type='multipart/form-data')
    assert b"File type not allowed" in response.data


def test_error_handling(test_client):
    """Test pour s'assurer que les erreurs ne révèlent pas d'informations sensibles."""
    response = test_client.get('/nonexistent-page')
    assert b"Internal Server Error" not in response.data  # Vérifier que les détails techniques ne sont pas exposés


def test_secure_session_cookie(test_client):
    """Test pour vérifier que les cookies de session sont sécurisés."""
    response = test_client.get('/')
    session_cookie = response.headers.get('Set-Cookie')
    assert 'HttpOnly' in session_cookie
    assert 'Secure' in session_cookie

def test_home_route(test_client):
    with test_client.application.app_context():
        response = test_client.get('/')
        assert response.status_code == 200
        assert b"Bienvenue sur Radiscool!" in response.data


def test_url_for_home(test_client):
    with test_client.application.app_context():
        url = url_for('home')
        assert url == '/'

