from flask import Flask, request, jsonify
import bcrypt
import json
import requests
import os
import math

app = Flask(__name__)

# Define paths for storage
STORAGE_DIR = "/app/data"
STORAGE_FILE = os.path.join(STORAGE_DIR, "storage.json")

# Ensure the data directory exists
if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

def load_storage():
    """Load storage data from the JSON file."""
    try:
        with open(STORAGE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_storage(data):
    """Save storage data to the JSON file."""
    with open(STORAGE_FILE, "w") as f:
        json.dump(data, f)

def calculate_entropy(password):
    """Calculate the entropy of the given password."""
    L = len(password)
    N = 95
    entropy = L * math.log2(N)
    return entropy

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    username = data["username"]
    email = data["email"]
    password = data["password"]

    # Check password entropy
    entropy = calculate_entropy(password)

    if entropy < 64:
        return jsonify({"error": "Password is too weak. Use a longer and more complex password."}), 400

    # Load storage and check for duplicates
    storage = load_storage()
    for user, details in storage.items():
        if user == username:
            return jsonify({"error": "Username already exists"}), 400
        if details["email"] == email:
            return jsonify({"error": "Email already exists"}), 400

    # Generate salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)

    # Send hashed password to Server2 for encryption
    response = requests.post("http://server2:5000/encrypt", json={"hash": hashed_password.decode("utf-8")})
    if response.status_code != 200:
        return jsonify({"error": "Encryption failed"}), 500

    encrypted_hash = response.json()["encrypted_hash"]

    # Save user data
    storage[username] = {
        "email": email,
        "salt": salt.decode("utf-8"),
        "password": encrypted_hash
    }
    save_storage(storage)

    return jsonify({"message": "Signup successful"}), 200

@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.json
        identifier = data.get("identifier")
        password = data.get("password")

        storage = load_storage()

        # Find user by username or email
        user = next(
            ({"username": k, "email": v["email"], "salt": v["salt"], "password": v["password"]}
             for k, v in storage.items() if k == identifier or v["email"] == identifier),
            None,
        )

        if not user:
            return jsonify({"error": "Username/email does not exist"}), 404

        # Compute hashed password
        salt = user["salt"].encode("utf-8")
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)

        # Validate hash using server2
        response = requests.post("http://server2:5000/validate", json={
            "hash": hashed_password.decode("utf-8"),
            "encrypted_hash": user["password"]
        })

        if response.status_code != 200 or not response.json().get("valid", False):
            return jsonify({"error": "Incorrect password"}), 403

        return jsonify({"username": user["username"], "email": user["email"]}), 200

    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)