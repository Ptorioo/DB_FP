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

            query = "SELECT article_id, title, created_at FROM ARTICLES;"
            cursor.execute(query)
            articles = cursor.fetchall()

            response = [
                {"article_id": article[0], "title": article[1], "created_at": article[2].isoformat()}
                for article in articles
            ]
            return response

        except Exception as e:
            error_response = json.dumps({"message": "An error occurred while fetching articles.", "details": str(e)})
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
