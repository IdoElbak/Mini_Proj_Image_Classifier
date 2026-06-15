import argparse
import jwt
import datetime
import time
import os
import json
from functools import wraps
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from google import genai
from google.genai import types

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-mini-project-key'

# --- GLOBALS ---
users = {}
revoked_tokens = set()
START_TIME = time.time()
jobs = {"success": 0, "fail": 0}

# Automatically track success/fail metrics for specific endpoints
@app.after_request
def track_jobs(response):
    if request.path in ['/register', '/login', '/logout', '/classifier']:
        if 200 <= response.status_code < 300:
            jobs["success"] += 1
        else:
            jobs["fail"] += 1
    return response

# Helper to format errors exactly as interface.md requires
def error_response(status_code, message):
    return jsonify({"error": {"http_status": status_code, "message": message}}), status_code

# Middleware decorator to protect endpoints
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return error_response(401, "Missing or invalid token")
        
        token = auth_header.split(" ")[1]
        if token in revoked_tokens:
            return error_response(401, "Missing or invalid token")
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['username']
        except Exception:
            return error_response(401, "Missing or invalid token")
        
        return f(current_user, *args, **kwargs)
    return decorated

# --- AUTH ENDPOINTS ---

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True)
    if not data or 'username' not in data or 'password' not in data:
        return error_response(400, "Malformed request")
    
    username = data['username']
    if username in users:
        return error_response(409, "User already exists")
    
    users[username] = generate_password_hash(data['password'])
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)
    if not data or 'username' not in data or 'password' not in data:
        return error_response(400, "Malformed request")
    
    user_pwd = users.get(data['username'])
    if not user_pwd or not check_password_hash(user_pwd, data['password']):
        return error_response(401, "Invalid username or password")
    
    token = jwt.encode({
        'username': data['username'],
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    }, app.config['SECRET_KEY'], algorithm="HS256")
    
    return jsonify({"token": token}), 200

@app.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    token = request.headers.get('Authorization').split(" ")[1]
    revoked_tokens.add(token)
    return jsonify({"message": "Logged out successfully"}), 200

# --- CLASSIFIER & STATUS ENDPOINTS ---

@app.route('/status', methods=['GET'])
@token_required
def status(current_user):
    uptime = round(time.time() - START_TIME, 1)
    # Health is 'ok' if the API key is present and inference can theoretically be done
    health = "ok" if os.environ.get("GEMINI_API_KEY") else "error"
    return jsonify({
        "status": {
            "uptime": uptime,
            "processed": jobs,
            "health": health,
            "api_version": 1
        }
    }), 200

@app.route('/classifier', methods=['POST'])
@token_required
def classifier(current_user):
    # Validate the file payload
    if 'image' not in request.files:
        return error_response(400, "Malformed request: missing 'image' field")
        
    file = request.files['image']
    if not file or file.filename == '':
        return error_response(400, "Malformed request: no file selected")
        
    if not (file.filename.lower().endswith('.png') or file.filename.lower().endswith('.jpeg')):
        return error_response(400, "Unsupported image format")
        
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return error_response(500, "Inference engine connection failed")

        client = genai.Client(api_key=api_key)
        image_bytes = file.read()
        
        # Enforce exact JSON response structure from the model
        prompt = (
            "Analyze this image and classify the primary object. "
            "Return ONLY a valid JSON object matching this exact format: "
            "{\"matches\": [{\"name\": \"object_name\", \"score\": 0.95}]} "
            "The scores must be strictly greater than 0.0, less than or equal to 1.0, and sum to 1.0 or less."
        )
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                prompt,
                types.Part.from_bytes(data=image_bytes, mime_type=file.mimetype)
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        
        result_json = json.loads(response.text)
        return jsonify(result_json), 200
        
    except Exception as e:
        error_msg = str(e).lower()
        
        if "400" in error_msg or "invalid" in error_msg or "decode" in error_msg:
            return error_response(400, "Malformed image data")
        return error_response(500, f"Internal server error: {str(e)}")

# Catch-all for unsupported methods
@app.errorhandler(405)
def method_not_allowed(e):
    return error_response(405, "Unsupported HTTP method")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Flask server.")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    app.run(debug=True, host="0.0.0.0", port=args.port)