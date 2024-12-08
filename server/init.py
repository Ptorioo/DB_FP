import socket
import threading
import signal
import json
import sys
from utils.connection import *
from utils.auth import *

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

                    match action:
                        case "register":
                            response = self.register_user(payload)
                        case "login":
                            response = self.login_user(payload)
                        case "get_articles":
                            response = self.get_all_articles(payload)
                        case "get_article":
                            response = self.get_article(payload)
                        case "create_comment":
                            response = self.create_comment(payload)
                        case "create_article":
                            response = self.create_article(payload)
                        case "report_article":
                            response = self.report_article(payload)
                        case "report_comment":
                            response = self.report_comment(payload)
                        case "is_following":
                            response = self.is_following(payload)
                        case "follow_user":
                            response = self.follow_user(payload)
                        case "unfollow_user":
                            response = self.unfollow_user(payload)
                        case "is_favorite":
                            response = self.is_favorite(payload)
                        case "favorite_article":
                            response = self.favorite_article(payload)
                        case "unfavorite_article":
                            response = self.unfavorite_article(payload)
                        case "get_favorites":
                            response = self.get_favorites(payload)
                        case "get_followings":
                            response = self.get_followings(payload)
                        case "update_email":
                            response = self.update_email(payload)
                        case "update_password":
                            response = self.update_password(payload)
                        case "search_article":
                            response = self.search_article(payload)
                        case "get_shared_count":
                            response = self.get_shared_count(payload)
                        case "share_article":
                            response = self.share_article(payload)
                        case _:
                            response = {"message": "Unknown action."}
                    
                    client_socket.send(json.dumps(response).encode('utf-8'))

                except json.JSONDecodeError:
                    error_message = {"message": "Invalid JSON format."}
                    client_socket.send(json.dumps(error_message).encode('utf-8'))

        finally:
            client_socket.close()

    def register_user(self, data):
        try:
            username = data["username"]
            password = data["password"]
            email = data["email"]

            if not all([username, password, email]):
                return {"message": "All fields (username, password, email) are required."}

            conn = self.db
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

            return {"message": "User registered successfully.", "user_id": user_id}

        except Exception as e:
            conn.rollback()
            return {"message": "An error occurred during registration.", "details": str(e)}

    def login_user(self, data):
        try:
            username = data["username"]
            password = data["password"]

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

            if stored_password != hash_password(password):
                return {"message": "Invalid password."}

            cursor.close()

            return {"message": "Login successful!", "user_id": user_id}

        except Exception as e:
            print(str(e))
            return {"message": "An error occurred during login.", "details": str(e)}

    def get_all_articles(self, data):
        try:
            conn = self.db
            cursor = conn.cursor()

            page = data.get("page", 1)
            size = data.get("size", 9)

            if page < 1 or size < 1:
                raise ValueError("Page and size must be positive integers.")

            offset = (page - 1) * size

            query = """
            SELECT a.article_id, a.title, u.username AS author, a.created_at
            FROM ARTICLES a
            JOIN USERS u ON a.author_id = u.user_id
            WHERE a.status != 'archived'
            ORDER BY a.created_at DESC
            LIMIT %s OFFSET %s;
            """
            cursor.execute(query, (size, offset))
            articles = cursor.fetchall()

            count_query = """
            SELECT COUNT(*)
            FROM ARTICLES
            WHERE status != 'archived';
            """
            cursor.execute(count_query)
            total_articles = cursor.fetchone()[0]
            total_pages = (total_articles + size - 1) // size

            response = {
                "articles": [
                    {"article_id": article[0], "title": article[1], "author": article[2], "created_at": article[3].isoformat()}
                    for article in articles
                ],
                "total_pages": total_pages
            }
            return response

        except Exception as e:
            error_response = {
                "message": "An error occurred while fetching articles.",
                "details": str(e)
            }
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
                au.user_id AS article_author_id,
                a.content AS article_content,
                a.created_at AS article_created_at,
                c.comment_id,
                cu.username AS comment_author,
                cu.user_id AS comment_author_id,
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
                "author_id": result[0][3],
                "content": result[0][4],
                "created_at": result[0][5].isoformat(),
                "comments": []
            }

            for row in result:
                if row[6] is not None:
                    comment = {
                        "comment_id": row[6],
                        "author": row[7],
                        "author_id": row[8],
                        "content": row[9],
                        "created_at": row[10].isoformat()
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
    
    def report_article(self, data):
        try:
            reporter_id = data["reporter_id"]
            target_article_id = data["target_article_id"]
            reason = data["reason"]

            query = """
            INSERT INTO REPORT_A (reporter_id, target_article_id, reason, created_at)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING report_article_id;
            """
            cursor = self.db.cursor()
            cursor.execute(query, (reporter_id, target_article_id, reason))
            report_article_id = cursor.fetchone()[0]
            self.db.commit()

            response = {
                "message": "Article reported successfully!"
            }
            return response

        except Exception as e:
            error_response = {
                "message": str(e)
            }
            return error_response

    def report_comment(self, data):
        try:
            reporter_id = data["reporter_id"]
            target_comment_id = data["target_comment_id"]
            reason = data["reason"]

            query = """
            INSERT INTO REPORT_C (reporter_id, target_comment_id, reason, created_at)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING report_comment_id;
            """
            cursor = self.db.cursor()
            cursor.execute(query, (reporter_id, target_comment_id, reason))
            report_comment_id = cursor.fetchone()[0]
            self.db.commit()

            response = {
                "message": "Comment reported successfully!"
            }
            return response

        except Exception as e:
            error_response = {
                "message": str(e)
            }
            return error_response
    
    def is_following(self, data):
        try:
            user_id = data["user_id"]
            author_id = data["author_id"]

            query = """
                SELECT EXISTS (
                    SELECT 1 
                    FROM USER_FOLLOWERS 
                    WHERE follower_id = %s AND followee_id = %s
                );
            """

            cursor = self.db.cursor()
            cursor.execute(query, (user_id, author_id))
            result = cursor.fetchone()[0]

            if result:
                response = {
                    "message": "User is following."
                }
            else:
                response = {
                    "message": "User is not following."
                }
            return response

        except Exception as e:
            error_response = {
                "message": str(e)
            }
            return error_response
    
    def follow_user(self, data):
        try:
            follower_id = data["follower_id"]
            followee_id = data["followee_id"]

            query = """
            INSERT INTO USER_FOLLOWERS (follower_id, followee_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING;
            """

            cursor = self.db.cursor()
            cursor.execute(query, (follower_id, followee_id))
            self.db.commit()

            response = {
                "message": "User is now following."
            }

            return response

        except Exception as e:
            error_response = {
                "message": str(e)
            }
            return error_response

    def unfollow_user(self, data):
        try:
            follower_id = data["follower_id"]
            followee_id = data["followee_id"]

            query = """
                DELETE FROM USER_FOLLOWERS 
                WHERE follower_id = %s AND followee_id = %s;
            """

            cursor = self.db.cursor()
            cursor.execute(query, (follower_id, followee_id))
            self.db.commit()

            response = {
                "message": "User is no longer following."
            }

            return response

        except Exception as e:
            error_response = {
                "message": str(e)
            }
            return error_response
    
    def is_favorite(self, data):
        try:
            user_id = data["user_id"]
            article_id = data["article_id"]

            query = """
                SELECT EXISTS (
                    SELECT 1 
                    FROM USER_FAVORITES
                    WHERE user_id = %s AND article_id = %s
                );
            """

            cursor = self.db.cursor()
            cursor.execute(query, (user_id, article_id))
            result = cursor.fetchone()[0]

            if result:
                response = {
                    "message": "User is favoriting."
                }
            else:
                response = {
                    "message": "User is not favoriting."
                }
            return response

        except Exception as e:
            error_response = {
                "message": str(e)
            }
            return error_response

    def favorite_article(self, data):
        try:
            user_id = data["user_id"]
            article_id = data["article_id"]

            query = """
            INSERT INTO USER_FAVORITES (user_id, article_id, saved_time)
            VALUES (%s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT DO NOTHING;
            """

            cursor = self.db.cursor()
            cursor.execute(query, (user_id, article_id))
            self.db.commit()

            response = {
                "message": "User is now favoriting."
            }

            return response

        except Exception as e:
            error_response = {
                "message": str(e)
            }
            return error_response

    def unfavorite_article(self, data):
        try:
            user_id = data["user_id"]
            article_id = data["article_id"]

            query = """
                DELETE FROM USER_FAVORITES 
                WHERE user_id = %s AND article_id = %s;
            """

            cursor = self.db.cursor()
            cursor.execute(query, (user_id, article_id))
            self.db.commit()

            response = {
                "message": "User is no longer favoriting."
            }

            return response

        except Exception as e:
            error_response = {
                "message": str(e)
            }
            return error_response
    
    def get_favorites(self, data):
        try:
            user_id = data

            query = """
                SELECT a.article_id, u.username AS author_username, a.title, a.created_at
                FROM USER_FAVORITES uf
                JOIN ARTICLES a ON uf.article_id = a.article_id
                JOIN USERS u ON a.author_id = u.user_id
                WHERE uf.user_id = %s;
            """

            cursor = self.db.cursor()
            cursor.execute(query, (user_id,))
            favorites = cursor.fetchall()

            result = [
                {
                    "article_id": row[0],
                    "author": row[1],
                    "title": row[2],
                    "created_at": row[3].isoformat()
                } for row in favorites
            ]

            return {
                "user_id": user_id,
                "favorites": result
            }
        
        except Exception as e:
            error_response = {
                "message": str(e)
            }
            return error_response

    def get_followings(self, data):
        try:
            user_id = data

            query = """
                SELECT a.article_id, u.username AS author_username, a.title, a.created_at
                FROM USER_FOLLOWERS uf
                JOIN ARTICLES a ON uf.followee_id = a.author_id
                JOIN USERS u ON a.author_id = u.user_id
                WHERE uf.follower_id = %s;
            """
            
            cursor = self.db.cursor()
            cursor.execute(query, (user_id,))
            followings = cursor.fetchall()

            result = [
                {
                    "article_id": row[0],
                    "author": row[1],
                    "title": row[2],
                    "created_at": row[3].isoformat()
                } for row in followings
            ]

            return {
                "user_id": user_id,
                "followings": result
            }

        except Exception as e:
            error_response = {
                "message": str(e)
            }
            return error_response
    
    def update_email(self, data):
        try:
            user_id = data["user_id"]
            new_email = data["new_email"]

            query = """
            UPDATE USERS
            SET email = %s
            WHERE user_id = %s;
            """

            cursor = self.db.cursor()
            cursor.execute(query, (new_email, user_id))
            self.db.commit()

            response = {
                    "message": "Email updated!"
                }

            return response

        except Exception as e:
            error_response = {
                "message": str(e)
            }
            return error_response
    
    def update_password(self, data):
        try:
            user_id = data["user_id"]
            new_password = data["new_password"]

            query = """
            UPDATE USERS
            SET password = %s
            WHERE user_id = %s;
            """

            cursor = self.db.cursor()
            cursor.execute(query, (new_password, user_id))
            self.db.commit()

            response = {
                    "message": "Password updated!"
                }

            return response

        except Exception as e:
            error_response = {
                "message": str(e)
            }
            return error_response

    def search_article(self, data):
        try:
            keyword = f"%{data}%"

            query = """
            SELECT article_id, a.title, u.username, a.created_at
            FROM ARTICLES a
            JOIN USERS u ON u.user_id = a.author_id
            WHERE a.title LIKE %s and a.status != 'archived';
            """

            cursor = self.db.cursor()
            cursor.execute(query, (keyword,))

            articles = cursor.fetchall()

            response = {
                "articles": [
                    {"article_id": article[0], "title": article[1], "author": article[2], "created_at": article[3].isoformat()}
                    for article in articles
                ]
            }
            
            return response

        except Exception as e:
            error_response = {
                "message": str(e)
            }
            return error_response

    def get_shared_count(self, data):
        try:
            article_id = data

            query = """
            SELECT COUNT(*) AS shared_count
            FROM USER_SHARED us
            WHERE us.article_id = %s;
            """

            cursor = self.db.cursor()
            cursor.execute(query, (article_id,))

            shared_count = cursor.fetchone()[0]

            response = {
                "shared_count": shared_count
            }

            return response

        except Exception as e:
            error_response = {
                "message": str(e)
            }
            return error_response

    def share_article(self, data):
        try:
            user_id = data["user_id"]
            article_id = data["article_id"]

            query = """
            INSERT INTO USER_SHARED (user_id, article_id, shared_at)
            VALUES (%s, %s, CURRENT_TIMESTAMP);
            """

            cursor = self.db.cursor()
            cursor.execute(query, (user_id, article_id))
            self.db.commit()

            response = {
                "message": "Article shared successfully!"
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

    def review_comment_report(self):
        try:
            query = """
            SELECT rc.report_comment_id, rc.reporter_id, rc.target_comment_id, rc.reason, rc.created_at, c.content
            FROM REPORT_C rc
            JOIN COMMENTS c ON rc.target_comment_id = c.comment_id
            WHERE rc.status = 'pending';
            """

            cursor = self.db.cursor()
            cursor.execute(query)
            reports_c = cursor.fetchall()

            result = [
                {
                    "report_comment_id": row[0],
                    "reporter_id": row[1],
                    "target_comment_id": row[2],
                    "reason": row[3],
                    "created_at": row[4].isoformat(),
                    "comment_content": row[5]
                } for row in reports_c
            ]

            response = {
                    "report comments": result
                }

            return response

        except Exception as e:
            error_response = {
                "message": str(e)
            }
            return error_response

    def update_comment_report(self, data):
        try:
            report_c_id = data["report_comment_id"]
            status = data["status"]
            query = """
            UPDATE REPORT_C
            SET status = %s
            WHERE report_comment_id = %s;
            """

            cursor = self.db.cursor()
            cursor.execute(query, (status, report_c_id))
            self.db.commit()

            response = {
                    "message": "Report update!"
                }

            return response

        except Exception as e:
            error_response = {
                "message": str(e)
            }
            return error_response

    def delete_comment(self, data):
        try:
            comment_id = data["comment_id"]
            query = """
            DELETE FROM COMMENTS
            WHERE comment_id = %s;
            """
    
            cursor = self.db.cursor()
            cursor.execute(query, (comment_id,))
            self.db.commit()
    
            response = {
                "message": "Comment deleted successfully!"
            }
            return response
    
        except Exception as e:
            error_response = {
                "message": str(e)
            }
            return error_response

    def review_article_report(self):
        try:
            query = """
            SELECT ra.report_article_id, ra.reporter_id, ra.target_article_id, ra.reason, ra.created_at, a.title, a.content
            FROM REPORT_A ra
            JOIN ARTICLES a ON ra.target_article_id = a.article_id
            WHERE ra.status = 'pending';
            """

            cursor = self.db.cursor()
            cursor.execute(query)
            reports_a = cursor.fetchall()

            result = [
                {
                    "report_article_id": row[0],
                    "reporter_id": row[1],
                    "target_comment_id": row[2],
                    "reason": row[3],
                    "created_at": row[4].isoformat(),
                    "article_title": row[5],
                    "article_content": row[6]
                } for row in reports_a
            ]

            response = {
                    "report articles": result
                }

            return response

        except Exception as e:
            error_response = {
                "message": str(e)
            }
            return error_response

    def update_article_report(self, data):
        try:
            report_a_id = data["report_article_id"]
            status = data["status"]
            query = """
            UPDATE REPORT_A
            SET status = %s
            WHERE report_article_id = %s;
            """

            cursor = self.db.cursor()
            cursor.execute(query, (status, report_a_id))
            self.db.commit()

            response = {
                    "message": "Report update!"
                }

            return response

        except Exception as e:
            error_response = {
                "message": str(e)
            }
            return error_response

    def delete_article(self, data):
        try:
            article_id = data["article_id"]
            query = """
            DELETE FROM ARTICLES
            WHERE article_id = %s;
            """
    
            cursor = self.db.cursor()
            cursor.execute(query, (article_id,))
            self.db.commit()
    
            response = {
                "message": "Article deleted successfully!"
            }
            return response
    
        except Exception as e:
            error_response = {
                "message": str(e)
            }
            return error_response

    def remove_user(self, data):
        try:
            user_id = data["user_id"]
            query = """
            DELETE FROM USER
            WHERE user_id = %s;
            """
            
            cursor = self.db.cursor()
            cursor.execute(query, (user_id))
            self.db.commit()

            response = {
                "message": "Delete successful!"
            }
            return response

        except Exception as e:
            error_response = {
                "message": str(e)
            }
            return error_response

    def update_user_status(self, data):
        try:
            user_id = data["user_id"]
            status = data["status"]
            query = """
            UPDATE USER
            SET status = %s
            WHERE user_id = %s
            """
            cursor = self.db.cursor()
            cursor.execute(query, (status, user_id))
            self.db.commit()
            response = {
                "message": "Update Successful!"
            }
            return response;
        except Exception as e:
            error_response = {
                "message": str(e)
            }
            return error_response

    def review_users(self, data):
        try:
            user_id = data["user_id"]
            query = """
            SELECT * FROM USERS
            WHERE user_id = %s 
            """
            cursor = self.db.cursor()
            cursor.execute(query, (user_id))
            user_info = cursor.fetchall()
            response = [{
                "user_id": row[0],
                "username": row[1],
                "email": row[3],
                "status": row[4],
                "report_count": row[5].isformat() 
            } for row in user_info
            ]
            return response
        
        except Exception as e:
            error_response = {
                "message": str(e)
            }
            return error_response

if __name__ == "__main__":
    server = TCPServer()
    server.start()
