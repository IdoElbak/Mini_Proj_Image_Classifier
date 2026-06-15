import requests

BASE_URL = "http://localhost:5000"

def test_status_success(auth_token):
    """
    Requests the server status using a valid authentication token.
    Verifies that the server returns a 200 OK and that the response contains
    valid uptime, health, API version, and a processed jobs dictionary.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.get(f"{BASE_URL}/status", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "uptime" in data["status"]
    assert "processed" in data["status"]
    assert "success" in data["status"]["processed"]
    assert "fail" in data["status"]["processed"]
    assert data["status"]["health"] in ["ok", "error"]
    assert data["status"]["api_version"] == 1

def test_status_unauthorized():
    """
    Requests the server status without an Authorization header.
    Verifies that the server blocks the request and returns a 401 Unauthorized.
    """
    response = requests.get(f"{BASE_URL}/status")
    assert response.status_code == 401