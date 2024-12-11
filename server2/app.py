# How to run: docker-compose up --build | docker-compose down | docker system prune -a
# Check files: docker exec -it password_storage_project-server1-1 /bin/bash

import base64
import os
from flask import Flask, request, jsonify
import tink
from tink import daead, cleartext_keyset_handle

app = Flask(__name__)

# Define the directory and path for storing the keyset
KEYSET_DIR = "/app/keys"
KEYSET_FILE = os.path.join(KEYSET_DIR, "keyset.json")

# Ensure the directory for the keyset exists
if not os.path.exists(KEYSET_DIR):
    os.makedirs(KEYSET_DIR)

# Initialize Tink with DAEAD and AES-SIV
try:
    daead.register()
    if not os.path.exists(KEYSET_FILE):
        # Generate a new keyset for AES-SIV if it doesn't exist
        keyset_handle = tink.new_keyset_handle(daead.deterministic_aead_key_templates.AES256_SIV)
        with open(KEYSET_FILE, "w") as keyset_file:
            cleartext_keyset_handle.write(
                tink.JsonKeysetWriter(keyset_file), keyset_handle
            )
    else:
        # Load the existing keyset
        with open(KEYSET_FILE, "r") as keyset_file:
            serialized_keyset = keyset_file.read()
            keyset_handle = cleartext_keyset_handle.read(
                tink.JsonKeysetReader(serialized_keyset)
            )

    daead_primitive = keyset_handle.primitive(daead.DeterministicAead)
except tink.TinkError as e:
    raise e

@app.route("/encrypt", methods=["POST"])
def encrypt():
    try:
        data = request.json
        if "hash" not in data:
            return jsonify({"error": "Missing 'hash' in request body"}), 400

        hash_to_encrypt = data["hash"].encode("utf-8")
        
        # Use DAEAD's encrypt_deterministically method
        encrypted_hash = daead_primitive.encrypt_deterministically(hash_to_encrypt, b"")

        encrypted_hash_b64 = base64.b64encode(encrypted_hash).decode("utf-8")
        return jsonify({"encrypted_hash": encrypted_hash_b64}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/validate", methods=["POST"])
def validate():
    try:
        data = request.json
        if "hash" not in data or "encrypted_hash" not in data:
            return jsonify({"error": "Missing 'hash' or 'encrypted_hash' in request body"}), 400#

        hash_to_validate = data["hash"].encode("utf-8")
        encrypted_hash_b64 = data["encrypted_hash"]

        # Use DAEAD's encrypt_deterministically method
        encrypted_hash_validate = daead_primitive.encrypt_deterministically(hash_to_validate, b"")

        encrypted_hash_validate_b64 = base64.b64encode(encrypted_hash_validate).decode("utf-8")

        valid = encrypted_hash_validate_b64 == encrypted_hash_b64
        return jsonify({"valid": valid}), 200
    except Exception as e:
        return jsonify({"error": "Decryption failed"}), 400


#@app.route("/validate", methods=["POST"])
#def validate():
#    try:
#        data = request.json
#        if "hash" not in data or "encrypted_hash" not in data:
#            return jsonify({"error": "Missing 'hash' or 'encrypted_hash' in request body"}), 400#
#
#        hash_to_validate = data["hash"].encode("utf-8")
#        encrypted_hash_b64 = data["encrypted_hash"]
#
#        encrypted_hash = base64.b64decode(encrypted_hash_b64)
#        # Use DAEAD's decrypt_deterministically method
#        decrypted_hash = daead_primitive.decrypt_deterministically(encrypted_hash, b"")
#
#        print(f"Decrypted Hash: {decrypted_hash.decode('utf-8')}", flush=True)
#
#        valid = hash_to_validate == decrypted_hash
#        print(f"Validation result: {valid}", flush=True)
#        return jsonify({"valid": valid}), 200
#    except Exception as e:
#        print(f"Validation error: {e}", flush=True)
#        return jsonify({"error": "Decryption failed"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True) 