from flask import Flask, request, jsonify
import hashlib
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DB_NAME = "DB_FP"
DB_USER = "postgres"
DB_HOST = "localhost"
DB_PASSWORD = os.getenv("PASSWORD")
DB_PORT = os.getenv("PORT")

def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def hash_password(password: str) -> str:
    sha1_hash = hashlib.sha1()
    
    sha1_hash.update(password.encode('utf-8'))
    
    return sha1_hash.hexdigest()[:20]

@app.route("/")
def home():
    return jsonify({})

@app.route('/register', methods=['POST'])
def register_user():
    data = request.json

    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not all([username, password, email]):
        return jsonify({"error": "All fields (username, password, email) are required."}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO USERS (username, password, email)
        VALUES (%s, %s, %s)
        RETURNING user_id;
        """
        cursor.execute(query, (username, hash_password(password), email))
        user_id = cursor.fetchone()[0]

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "User registered successfully.", "user_id": user_id}), 201

    except psycopg2.IntegrityError as e:
        conn.rollback()
        if "username" in str(e):
            return jsonify({"error": "Username already exists."}), 409
        if "email" in str(e):
            return jsonify({"error": "Email already exists."}), 409
        return jsonify({"error": "Integrity error occurred."}), 500

    except Exception as e:
        return jsonify({"error": "An error occurred during registration.", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=8080)
