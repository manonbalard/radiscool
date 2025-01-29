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


def test_error_handling(test_client):
    """Test to ensure that errors do not reveal sensitive information."""
    response = test_client.get("/nonexistent-page")
    assert (
        b"Internal Server Error" not in response.data
    )  # Verify that technical details are not exposed
