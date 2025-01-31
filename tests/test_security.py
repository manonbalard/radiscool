def test_sql_injection(test_client):
    """
    Test to check protection against SQL injection.

    This test attempts to log in using an SQL injection payload and verifies
    that the application does not grant unauthorized access.
    """
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
    """
    Test to ensure weak passwords are rejected during signup.

    This test attempts to sign up with a weak password and checks if the application
    enforces strong password policies.
    """
    # Perform a GET request to load the signup page
    followup_response = test_client.get("/signup")
    assert followup_response.status_code == 200

    # Perform the POST request with a weak password
    response = test_client.post(
        "/signup", data={"email": "test@example.com", "password": "123"}
    )

    # Verify that the response is a redirection (HTTP status 302)
    assert response.status_code == 302  # Expected redirection

    # Verify that the user is redirected to the signup page after failure
    assert response.location.endswith("/signup")  # Redirect to /signup on failure

    # Verify that the error message "Password is too weak" is in the response
    followup_response = test_client.get("/signup")
    assert (
        b"Password is too weak" in followup_response.data
    )  # Verify error message presence


def test_error_handling(test_client):
    """
    Test to ensure that errors do not reveal sensitive information.

    This test accesses a non-existent page and verifies that technical details
    are not exposed in the error response.
    """
    response = test_client.get("/nonexistent-page")
    assert (
        b"Internal Server Error" not in response.data
    )  # Verify that technical details are not exposed
