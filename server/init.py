import socket
import threading
import signal
import json
import sys
from utils.connection import *

SERVER_IP = '127.0.0.1'
SERVER_PORT = 8080

class TCPServer:
    def __init__(self, host=SERVER_IP, port=SERVER_PORT):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True
        self.db = None

    def start(self):
        try:
            self.db = db_connect()
            print("Database connected.")

            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            print(f"Server listening on {self.host}:{self.port}")

            signal.signal(signal.SIGINT, self.shutdown)

            while self.running:
                try:
                    self.server_socket.settimeout(1.0)
                    client_socket, client_address = self.server_socket.accept()
                    print(f"Connection established with {client_address}")
                    threading.Thread(target=self.handle_client, args=(client_socket,)).start()
                except socket.timeout:
                    continue

        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.stop()

    def handle_client(self, client_socket):
        try:
            welcome_message = ("*****Please select a method to continue*****\n"
                            "0 [EXIT] Exit from the platform\n"
                            "1 [REGISTER] Register a user\n"
                            "2 [LOGIN] Log in to the platform\n")
            client_socket.send(welcome_message.encode('utf-8'))

            while True:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break

                try:
                    request = json.loads(data)
                    action = request.get("action")
                    payload = request.get("data")

                    if action == "register":
                        response = self.register_user(payload)
                    elif action == "login":
                        response = self.login_user(payload)
                    elif action == "get_articles":
                        response = self.get_all_articles()
                    elif action == "get_article":
                        response = self.get_article(payload)
                    elif action == "create_comment":
                        response = self.create_comment(payload)
                    elif action == "create_article":
                        response = self.create_article(payload)
                    else:
                        response = {"message": "Unknown action."}
                    
                    client_socket.send(json.dumps(response).encode('utf-8'))

                except json.JSONDecodeError:
                    error_message = {"message": "Invalid JSON format."}
                    client_socket.send(json.dumps(error_message).encode('utf-8'))

        finally:
            client_socket.close()

    def register_user(self, data):
        try:
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')

            if not all([username, password, email]):
                return {"message": "All fields (username, password, email) are required."}

            conn = self.db
            cursor = conn.cursor()

            user_query = """
            INSERT INTO USERS (username, password, email)
            VALUES (%s, %s, %s)
            RETURNING user_id;
            """
            cursor.execute(user_query, (username, password, email))
            user_id = cursor.fetchone()[0]

            role_query = """
            INSERT INTO USER_ROLE (user_id, role)
            VALUES (%s, 'User');
            """
            cursor.execute(role_query, (user_id,))
            conn.commit()
            cursor.close()

            return {"message": "User registered successfully.", "user_id": user_id}

        except Exception as e:
            conn.rollback()
            return {"message": "An error occurred during registration.", "details": str(e)}

    def login_user(self, data):
        try:
            username = data.get('username')
            password = data.get('password')

            if not all([username, password]):
                return {"message": "Both username and password are required."}

            conn = self.db
            cursor = conn.cursor()

            query = """
            SELECT user_id, password FROM USERS WHERE username = %s;
            """
            cursor.execute(query, (username,))
            result = cursor.fetchone()

            if not result:
                return {"message": "User not found."}

            user_id, stored_password = result

            if stored_password != password:
                return {"message": "Invalid password."}

            cursor.close()

            return {"message": "Login successful!", "user_id": user_id}

        except Exception as e:
            print(str(e))
            return {"message": "An error occurred during login.", "details": str(e)}

    def get_all_articles(self):
        try:
            conn = self.db
            cursor = conn.cursor()

            query = """
            SELECT a.article_id, a.title, u.username AS author, a.created_at
            FROM ARTICLES a
            JOIN USERS u ON a.author_id = u.user_id;
            """
            cursor.execute(query)
            articles = cursor.fetchall()

            response = [
                {"article_id": article[0], "title": article[1], "author": article[2], "created_at": article[3].isoformat()}
                for article in articles
            ]
            return response

        except Exception as e:
            error_response = json.dumps({"message": "An error occurred while fetching articles.", "details": str(e)})
            return error_response

    def get_article(self, data):
        try:
            conn = self.db
            cursor = conn.cursor()

            query = """
            SELECT 
                a.article_id,
                a.title AS article_title,
                au.username AS article_author,
                a.content AS article_content,
                a.created_at AS article_created_at,
                c.comment_id,
                cu.username AS comment_author,
                c.content AS comment_content,
                c.created_at AS comment_created_at
            FROM 
                ARTICLES a
            JOIN 
                USERS au ON a.author_id = au.user_id
            LEFT JOIN 
                COMMENTS c ON c.article_id = a.article_id
            LEFT JOIN 
                USERS cu ON c.owner_id = cu.user_id
            WHERE 
                a.article_id = %s
            ORDER BY 
                c.created_at;
            """
            cursor.execute(query, (data,))
            result = cursor.fetchall()

            article = {
                "article_id": result[0][0],
                "title": result[0][1],
                "author": result[0][2],
                "content": result[0][3],
                "created_at": result[0][4].isoformat(),
                "comments": []
            }

            for row in result:
                if row[5] is not None:
                    comment = {
                        "comment_id": row[5],
                        "author": row[6],
                        "content": row[7],
                        "created_at": row[8].isoformat()
                    }
                    article['comments'].append(comment)

            return article

        except Exception as e:
            error_response = json.dumps({"message": "An error occurred while fetching article details and comments.", "details": str(e)})
            return error_response
    
    def create_comment(self, data):
        try:
            article_id = data["article_id"]
            owner_id = data["owner_id"]
            content = data["content"]

            query = """
            INSERT INTO COMMENTS (article_id, owner_id, content, created_at)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING comment_id;
            """
            cursor = self.db.cursor()
            cursor.execute(query, (article_id, owner_id, content))
            comment_id = cursor.fetchone()[0]
            self.db.commit()

            response = {
                "message": "Comment created successfully!"
            }
            return response

        except Exception as e:
            error_response = {
                "message": str(e)
            }
            return error_response
    
    def create_article(self, data):
        try:
            author_id = data["author_id"]
            title = data["title"]
            content = data["content"]

            query = """
            INSERT INTO ARTICLES (author_id, title, content, created_at)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING article_id;
            """
            cursor = self.db.cursor()
            cursor.execute(query, (author_id, title, content))
            article_id = cursor.fetchone()[0]
            self.db.commit()

            response = {
                "message": "Article created successfully!"
            }
            return response

        except Exception as e:
            error_response = {
                "message": str(e)
            }
            return error_response

    def shutdown(self, signum, frame):
        print("\nShutting down the server...")
        self.running = False

    def stop(self):
        if self.server_socket:
            self.server_socket.close()
        if self.db:
            self.db.close()
        print("Server stopped.")

if __name__ == "__main__":
    server = TCPServer()
    server.start()
