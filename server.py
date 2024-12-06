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

        user_query = """
        INSERT INTO USERS (username, password, email)
        VALUES (%s, %s, %s)
        RETURNING user_id;
        """
        cursor.execute(user_query, (username, hash_password(password), email))
        user_id = cursor.fetchone()[0]

        role_query = """
        INSERT INTO USER_ROLE (user_id, role)
        VALUES (%s, 'User');
        """
        cursor.execute(role_query, (user_id,))

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


@app.route('/login', methods=['POST'])
def login_user():
    data = request.json

    username = data.get('username')
    password = data.get('password')

    if not all([username, password]):
        return jsonify({"error": "Both username and password are required."}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        SELECT user_id, password FROM USERS WHERE username = %s;
        """
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        if not result:
            return jsonify({"error": "User not found."}), 404

        user_id, stored_password = result

        if stored_password != hash_password(password):
            return jsonify({"error": "Invalid password."}), 401

        cursor.close()
        conn.close()

        return jsonify({"message": "Login successful!", "user_id": user_id}), 201

    except Exception as e:
        return jsonify({"error": "An error occurred during login.", "details": str(e)}), 500

@app.route('/articles', methods=['GET'])
def get_all_articles():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        SELECT a.article_id, u.username, a.title, a.created_at
        FROM ARTICLES a
        JOIN USERS u ON a.author_id = u.user_id;
        """
        cursor.execute(query)
        articles = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify([
            {"article_id": article[0], "title": article[1], "created_at": article[2].isoformat()}
            for article in articles
        ]), 200

    except Exception as e:
        return jsonify({"error": "An error occurred while fetching articles.", "details": str(e)}), 500


@app.route('/articles/<int:article_id>', methods=['GET'])
def get_article_with_comments(article_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        article_query = """
        SELECT title, content, created_at FROM ARTICLES WHERE article_id = %s;
        """
        cursor.execute(article_query, (article_id,))
        article = cursor.fetchone()

        if not article:
            return jsonify({"error": "Article not found."}), 404

        comments_query = """
        SELECT c.comment_id, u.username, c.content, c.created_at, c.parent_comment_id 
        FROM COMMENTS c 
        JOIN USERS u
        WHERE c.owner_id = u.user_id AND article_id = %s AND status = 'active';
        """
        cursor.execute(comments_query, (article_id,))
        comments = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            "article": {
                "title": article[0],
                "content": article[1],
                "created_at": article[2].isoformat()
            },
            "comments": [
                {
                    "comment_id": comment[0],
                    "owner_id": comment[1],
                    "content": comment[2],
                    "created_at": comment[3].isoformat(),
                    "parent_comment_id": comment[4]
                }
                for comment in comments
            ]
        }), 200

    except Exception as e:
        return jsonify({"error": "An error occurred while fetching the article.", "details": str(e)}), 500

@app.route('/articles/<int:article_id>/comments', methods=['POST'])
def add_comment(article_id):
    data = request.json

    owner_id = data.get('owner_id')
    content = data.get('content')
    parent_comment_id = data.get('parent_comment_id', None)

    if not all([owner_id, content]):
        return jsonify({"error": "Both owner_id and content are required."}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        article_query = "SELECT article_id FROM ARTICLES WHERE article_id = %s;"
        cursor.execute(article_query, (article_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Article not found."}), 404

        owner_query = "SELECT user_id FROM USERS WHERE user_id = %s;"
        cursor.execute(owner_query, (owner_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Owner not found."}), 404

        if parent_comment_id:
            parent_comment_query = "SELECT comment_id FROM COMMENTS WHERE comment_id = %s;"
            cursor.execute(parent_comment_query, (parent_comment_id,))
            if not cursor.fetchone():
                return jsonify({"error": "Parent comment not found."}), 404

        comment_query = """
        INSERT INTO COMMENTS (owner_id, article_id, parent_comment_id, content)
        VALUES (%s, %s, %s, %s)
        RETURNING comment_id, created_at;
        """
        cursor.execute(comment_query, (owner_id, article_id, parent_comment_id, content))
        comment_id, created_at = cursor.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "message": "Comment added successfully!",
            "comment": {
                "comment_id": comment_id,
                "article_id": article_id,
                "owner_id": owner_id,
                "content": content,
                "parent_comment_id": parent_comment_id,
                "created_at": created_at.isoformat()
            }
        }), 201

    except Exception as e:
        return jsonify({"error": "An error occurred while adding the comment.", "details": str(e)}), 500

@app.route('/reports/article', methods=['POST'])
def report_article():
    data = request.json

    reporter_id = data.get('reporter_id')
    target_article_id = data.get('target_article_id')
    reason = data.get('reason')

    if not all([reporter_id, target_article_id, reason]):
        return jsonify({"error": "All fields (reporter_id, target_article_id, reason) are required."}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        reporter_query = "SELECT user_id FROM USERS WHERE user_id = %s;"
        cursor.execute(reporter_query, (reporter_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Reporter not found."}), 404

        article_query = "SELECT article_id FROM ARTICLES WHERE article_id = %s;"
        cursor.execute(article_query, (target_article_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Target article not found."}), 404

        report_query = """
        INSERT INTO REPORT_A (reporter_id, target_article_id, reason)
        VALUES (%s, %s, %s)
        RETURNING report_article_id, created_at;
        """
        cursor.execute(report_query, (reporter_id, target_article_id, reason))
        report_article_id, created_at = cursor.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "message": "Article report submitted successfully!",
            "report": {
                "report_article_id": report_article_id,
                "reporter_id": reporter_id,
                "target_article_id": target_article_id,
                "reason": reason,
                "created_at": created_at.isoformat()
            }
        }), 201

    except Exception as e:
        return jsonify({"error": "An error occurred while reporting the article.", "details": str(e)}), 500


@app.route('/reports/comment', methods=['POST'])
def report_comment():
    data = request.json

    reporter_id = data.get('reporter_id')
    target_comment_id = data.get('target_comment_id')
    reason = data.get('reason')

    if not all([reporter_id, target_comment_id, reason]):
        return jsonify({"error": "All fields (reporter_id, target_comment_id, reason) are required."}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        reporter_query = "SELECT user_id FROM USERS WHERE user_id = %s;"
        cursor.execute(reporter_query, (reporter_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Reporter not found."}), 404

        comment_query = "SELECT comment_id FROM COMMENTS WHERE comment_id = %s;"
        cursor.execute(comment_query, (target_comment_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Target comment not found."}), 404

        report_query = """
        INSERT INTO REPORT_C (reporter_id, target_comment_id, reason)
        VALUES (%s, %s, %s)
        RETURNING report_comment_id, created_at;
        """
        cursor.execute(report_query, (reporter_id, target_comment_id, reason))
        report_comment_id, created_at = cursor.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "message": "Comment report submitted successfully!",
            "report": {
                "report_comment_id": report_comment_id,
                "reporter_id": reporter_id,
                "target_comment_id": target_comment_id,
                "reason": reason,
                "created_at": created_at.isoformat()
            }
        }), 201

    except Exception as e:
        return jsonify({"error": "An error occurred while reporting the comment.", "details": str(e)}), 500

@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        user_query = "SELECT user_id FROM USERS WHERE user_id = %s;"
        cursor.execute(user_query, (user_id,))
        if not cursor.fetchone():
            return jsonify({"error": "User not found."}), 404

        favorites_query = """
        SELECT a.article_id, a.title, uf.saved_time 
        FROM USER_FAVORITES uf
        JOIN ARTICLES a ON uf.article_id = a.article_id
        WHERE uf.user_id = %s;
        """
        cursor.execute(favorites_query, (user_id,))
        favorites = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify([
            {"article_id": article[0], "title": article[1], "saved_time": article[2].isoformat()}
            for article in favorites
        ]), 200

    except Exception as e:
        return jsonify({"error": "An error occurred while fetching favorites.", "details": str(e)}), 500


@app.route('/users/<int:user_id>/favorites', methods=['POST'])
def add_to_favorites(user_id):
    data = request.json

    article_id = data.get('article_id')

    if not article_id:
        return jsonify({"error": "Article ID is required."}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        user_query = "SELECT user_id FROM USERS WHERE user_id = %s;"
        cursor.execute(user_query, (user_id,))
        if not cursor.fetchone():
            return jsonify({"error": "User not found."}), 404

        article_query = "SELECT article_id FROM ARTICLES WHERE article_id = %s;"
        cursor.execute(article_query, (article_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Article not found."}), 404

        insert_query = """
        INSERT INTO USER_FAVORITES (user_id, article_id)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING;
        """
        cursor.execute(insert_query, (user_id, article_id))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Article added to favorites successfully!"}), 201

    except Exception as e:
        return jsonify({"error": "An error occurred while adding to favorites.", "details": str(e)}), 500

@app.route('/users/<int:user_id>/follow', methods=['POST'])
def follow_user(user_id):
    data = request.json

    followee_id = data.get('followee_id')

    if not followee_id:
        return jsonify({"error": "Followee ID is required."}), 400

    if user_id == followee_id:
        return jsonify({"error": "A user cannot follow themselves."}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        follower_query = "SELECT user_id FROM USERS WHERE user_id = %s;"
        cursor.execute(follower_query, (user_id,))
        if not cursor.fetchone():
            return jsonify({"error": "User not found."}), 404

        followee_query = "SELECT user_id FROM USERS WHERE user_id = %s;"
        cursor.execute(followee_query, (followee_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Followee not found."}), 404

        follow_query = """
        INSERT INTO USER_FOLLOWERS (follower_id, followee_id)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING;
        """
        cursor.execute(follow_query, (user_id, followee_id))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Followed the user successfully!"}), 201

    except Exception as e:
        return jsonify({"error": "An error occurred while following the user.", "details": str(e)}), 500


@app.route('/users/<int:user_id>/followers', methods=['GET'])
def get_user_followers(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        user_query = "SELECT user_id FROM USERS WHERE user_id = %s;"
        cursor.execute(user_query, (user_id,))
        if not cursor.fetchone():
            return jsonify({"error": "User not found."}), 404

        followers_query = """
        SELECT uf.follower_id, u.username
        FROM USER_FOLLOWERS uf
        JOIN USERS u ON uf.follower_id = u.user_id
        WHERE uf.followee_id = %s;
        """
        cursor.execute(followers_query, (user_id,))
        followers = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify([
            {"follower_id": follower[0], "username": follower[1]}
            for follower in followers
        ]), 200

    except Exception as e:
        return jsonify({"error": "An error occurred while fetching followers.", "details": str(e)}), 500


@app.route('/users/<int:user_id>/followings', methods=['GET'])
def get_user_followings(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        user_query = "SELECT user_id FROM USERS WHERE user_id = %s;"
        cursor.execute(user_query, (user_id,))
        if not cursor.fetchone():
            return jsonify({"error": "User not found."}), 404

        followings_query = """
        SELECT uf.followee_id, u.username
        FROM USER_FOLLOWERS uf
        JOIN USERS u ON uf.followee_id = u.user_id
        WHERE uf.follower_id = %s;
        """
        cursor.execute(followings_query, (user_id,))
        followings = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify([
            {"followee_id": following[0], "username": following[1]}
            for following in followings
        ]), 200

    except Exception as e:
        return jsonify({"error": "An error occurred while fetching followings.", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=8080)
