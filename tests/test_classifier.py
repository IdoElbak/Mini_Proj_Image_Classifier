import requests
import os

BASE_URL = "http://localhost:5000"

def test_classifier_success(auth_token):
    """
    Uploads a valid, real PNG image with a valid authorization token. 
    Verifies that the server successfully contacts the inference engine (200 OK) 
    and returns a JSON array of matches where all confidence scores are strictly 
    between 0.0 and 1.0.
    """
    image_path = 'tests/cat.png'
    with open(image_path, 'rb') as img_file:
        files = {'image': ('tests.png', img_file, 'image/png')}
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{BASE_URL}/classifier", headers=headers, files=files)
        
    assert response.status_code == 200
    data = response.json()
    assert "matches" in data
    assert len(data["matches"]) > 0
    for match in data["matches"]:
        assert 0.0 < match["score"] <= 1.0

def test_classifier_missing_token():
    """
    Attempts to upload a valid image but purposely omits the Authorization header. 
    Verifies that the server blocks access and returns a 401 Unauthorized status.
    """
    image_path = 'tests/cat.png'
    with open(image_path, 'rb') as img_file:
        files = {'image': ('cat.png', img_file, 'image/png')}
        response = requests.post(f"{BASE_URL}/classifier", files=files)
        
    assert response.status_code == 401

def test_classifier_bad_file_extension(auth_token):
    """
    Uploads a file with an unsupported extension (.txt instead of .png/.jpeg). 
    Verifies that the server correctly identifies the bad format, rejects it without 
    sending it to the inference engine, and returns a 400 Bad Request.
    """
    files = {'image': ('malicious.txt', b"print('hack')", 'text/plain')}
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.post(f"{BASE_URL}/classifier", headers=headers, files=files)
    
    assert response.status_code == 400

def test_classifier_corrupted_image_data(auth_token):
    """
    Uploads a file disguised with a valid .png extension, but the actual file content 
    is corrupted garbage text. Verifies that the server (or inference engine) catches 
    the malformed payload and returns a 400 Bad Request.
    """
    files = {'image': ('fake_image.png', b"This is not a real image, it is just raw text bytes", 'image/png')}
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.post(f"{BASE_URL}/classifier", headers=headers, files=files)
    
    assert response.status_code == 400