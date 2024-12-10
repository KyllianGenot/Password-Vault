from flask import Flask, request, jsonify
import bcrypt
import json
import requests
import os

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

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    username = data["username"]
    email = data["email"]
    password = data["password"]

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
    print(f"Computed Hash for bcrypt (Signup): {hashed_password}", flush=True)

    # Send hashed password to Server2 for encryption
    response = requests.post("http://server2:5000/encrypt", json={"hash": hashed_password.decode("utf-8")})
    if response.status_code != 200:
        return jsonify({"error": "Encryption failed"}), 500

    encrypted_hash = response.json()["encrypted_hash"]
    print(f"Encrypted Hash Received (Signup): {encrypted_hash}", flush=True)

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
        identifier = data.get("identifier")  # Username or email
        password = data.get("password")

        storage = load_storage()

        # Find user by username or email
        user = next(
            ({"username": k, "email": v["email"], "salt": v["salt"], "password": v["password"]}
             for k, v in storage.items() if k == identifier or v["email"] == identifier),
            None,
        )

        if not user:
            # User not found
            return jsonify({"error": "Username/email does not exist"}), 404

        # Compute hashed password
        salt = user["salt"].encode("utf-8")
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
        print(f"Computed Hash for bcrypt (Login): {hashed_password}", flush=True)

        # Validate hash using server2
        response = requests.post("http://server2:5000/validate", json={
            "hash": hashed_password.decode("utf-8"),
            "encrypted_hash": user["password"]
        })

        if response.status_code != 200 or not response.json().get("valid", False):
            # Password is incorrect
            return jsonify({"error": "Incorrect password"}), 403

        # Login successful
        return jsonify({"username": user["username"], "email": user["email"]}), 200

    except Exception as e:
        print(f"Login error: {str(e)}", flush=True)
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)