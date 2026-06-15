import requests
import uuid

BASE_URL = "http://localhost:5000"

def test_interop_register_missing_password():
    """Catches servers that don't validate missing payload fields (Expected 400)"""
    response = requests.post(f"{BASE_URL}/register", json={"username": f"user_{uuid.uuid4().hex[:8]}"})
    assert response.status_code == 400
    assert response.json()["error"]["http_status"] == 400

def test_interop_login_wrong_method():
    """Catches servers that don't restrict HTTP methods strictly to POST (Expected 405)"""
    response = requests.get(f"{BASE_URL}/login")
    assert response.status_code == 405
    assert response.json()["error"]["http_status"] == 405

def test_interop_status_invalid_bearer_format():
    """Catches servers that poorly parse the Authorization header string (Expected 401)"""
    # Notice the missing space after Bearer
    headers = {"Authorization": "BearerToken12345"} 
    response = requests.get(f"{BASE_URL}/status", headers=headers)
    assert response.status_code == 401
    assert response.json()["error"]["http_status"] == 401

def test_interop_classifier_malformed_image_content():
    """Catches servers that rely only on the .png extension but don't verify if it's decodable (Expected 400)"""
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(f"{BASE_URL}/register", json={"username": username, "password": "123"})
    resp = requests.post(f"{BASE_URL}/login", json={"username": username, "password": "123"})
    token = resp.json().get("token", "")

    headers = {"Authorization": f"Bearer {token}"}
    # Sending raw text disguised as a PNG
    files = {'image': ('corrupt.png', b"This is just raw text bytes, not a real image.", 'image/png')}
    response = requests.post(f"{BASE_URL}/classifier", headers=headers, files=files)
    
    assert response.status_code == 400
    assert response.json()["error"]["http_status"] == 400

def test_interop_status_type_validation():
    """Catches servers that return incorrectly typed JSON data according to interface.md (Expected 200)"""
    username = f"user_{uuid.uuid4().hex[:8]}"
    requests.post(f"{BASE_URL}/register", json={"username": username, "password": "123"})
    resp = requests.post(f"{BASE_URL}/login", json={"username": username, "password": "123"})
    token = resp.json().get("token", "")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/status", headers=headers)

    assert response.status_code == 200
    data = response.json()["status"]
    
    # interface.md dictates uptime must be a number, health must be ok/error, and api_version must be 1
    assert isinstance(data["uptime"], (int, float))
    assert data["health"] in ["ok", "error"]
    assert data["api_version"] == 1