import requests
import uuid

BASE_URL = "http://localhost:5000"

def generate_user():
    return f"user_{uuid.uuid4().hex[:8]}", "password123"

def test_register_success():
    """
    Attempts to register a new user with valid credentials.
    Verifies that the server creates the user and returns a 201 Created.
    """
    username, password = generate_user()
    response = requests.post(f"{BASE_URL}/register", json={"username": username, "password": password})
    assert response.status_code == 201
    assert response.json()["message"] == "User registered successfully"

def test_register_conflict():
    """
    Attempts to register a user that already exists.
    Verifies that the server catches the duplicate and returns a 409 Conflict.
    """
    username, password = generate_user()
    requests.post(f"{BASE_URL}/register", json={"username": username, "password": password})
    response = requests.post(f"{BASE_URL}/register", json={"username": username, "password": password})
    assert response.status_code == 409

def test_register_malformed():
    """
    Attempts to register a user but omits the password field.
    Verifies that the server identifies the missing data and returns a 400 Bad Request.
    """
    response = requests.post(f"{BASE_URL}/register", json={"username": "only_username"})
    assert response.status_code == 400

def test_login_success():
    """
    Attempts to log in with a valid, registered account.
    Verifies that the server accepts the credentials and returns a 200 OK with a session token.
    """
    username, password = generate_user()
    requests.post(f"{BASE_URL}/register", json={"username": username, "password": password})
    response = requests.post(f"{BASE_URL}/login", json={"username": username, "password": password})
    assert response.status_code == 200
    assert "token" in response.json()

def test_login_unauthorized():
    """
    Attempts to log in with an incorrect password.
    Verifies that the server denies access and returns a 401 Unauthorized.
    """
    username, password = generate_user()
    requests.post(f"{BASE_URL}/register", json={"username": username, "password": password})
    response = requests.post(f"{BASE_URL}/login", json={"username": username, "password": "wrongpassword"})
    assert response.status_code == 401

def test_logout_success(auth_token):
    """
    Attempts to log out using a valid active session token.
    Verifies that the server invalidates the token and returns a 200 OK.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.post(f"{BASE_URL}/logout", headers=headers)
    assert response.status_code == 200