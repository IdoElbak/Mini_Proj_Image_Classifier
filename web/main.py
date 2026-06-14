import argparse
import jwt
import datetime
from functools import wraps
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-mini-project-key'

# In-memory data stores
users = {}
revoked_tokens = set()

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

# --- ENDPOINTS ---

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
    
    # Generate a token valid for 1 hour
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

# Catch-all for unsupported methods on these specific routes
@app.errorhandler(405)
def method_not_allowed(e):
    return error_response(405, "Unsupported HTTP method")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Flask server.")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    app.run(debug=True, host="0.0.0.0", port=args.port)