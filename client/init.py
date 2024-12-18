import socket
import os
import json
from action.register import *
from action.login import *
from action.view_article import *
from action.create_article import *
from action.view_profile import *
from action.search_article import *
from action.view_report_a import *
from action.view_report_c import *
from action.manage_user import *

SERVER_IP = '127.0.0.1'
SERVER_PORT = 8080

PAGE_SIZE = 9

class TCPClient:
    def __init__(self, host=SERVER_IP, port=SERVER_PORT):
        self.host = host
        self.port = port
        self.current_user = None
        self.current_user_id = None
        self.current_user_role = None

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.host, self.port))

            welcome_message = client_socket.recv(1024).decode('utf-8')

            while not self.current_user:
                os.system('cls' if os.name == 'nt' else 'clear')
                print(welcome_message)
                
                command = input(">>>")
                match command:
                    case "0" | "exit":
                        print("See you later!")
                        break

                    case "1" | "register":
                        register_info = register_user()
                        client_socket.send(json.dumps({"action": "register", "data": register_info}).encode('utf-8'))

                        response = client_socket.recv(1024).decode('utf-8')
                        response_data = json.loads(response)
                        print(response_data.get("message", "No message received"))
                        input("\nPress any key to continue...")

                    case "2" | "login":
                        login_info = login_user()
                        client_socket.send(json.dumps({"action": "login", "data": login_info}).encode('utf-8'))

                        response = client_socket.recv(1024).decode('utf-8')
                        response_data = json.loads(response)
                        print(response_data.get("message", "No message received"))

                        if response_data.get("message") == "Login successful!":
                            self.current_user = login_info["username"]
                            self.current_user_id = response_data["user_id"]
                            self.current_user_role = response_data["user_role"]
                            break

                        input("\nPress any key to continue...")
            
            current_page = 1
            while self.current_user:
                os.system('cls' if os.name == 'nt' else 'clear')
                print("***** Welcome *****")

                client_socket.send(json.dumps({
                    "action": "get_articles",
                    "data": {"page": current_page, "size": PAGE_SIZE}
                }).encode('utf-8'))
                response = client_socket.recv(8192).decode('utf-8')
                response_data = json.loads(response)

                articles = response_data.get("articles", [])
                total_pages = response_data.get("total_pages", 1)

                if not articles:
                    print("No articles found.")
                else:
                    for idx, article in enumerate(articles, start=1 + (current_page - 1) * PAGE_SIZE):
                        print(f"[{idx}] {article['title']} by {article['author']} {article['created_at']}")

                print("\n0 [LOGOUT] Log out from the platform")
                print("Z [PREVIOUS] View previous page")
                print("X [NEXT] View next page")
                print("C [CREATE] Create an article")
                print("P [PROFILE] View user profile")
                print("Q [SEARCH] Search article")
                if self.current_user_role == "Admin":
                    print("V [VIEW_A] View reported articles")
                    print("M [MANAGE] Manage users")
                    print("W [VIEW_C] View reported comments")
                print("\nOr select an article by its number.")

                command = input(f"[{self.current_user}] >>>").strip().lower()

                match command:
                    case "0" | "logout":
                        print("Logging out...")
                        break
                    case "c" | "create":
                        article = create_article(self.current_user_id)
                        client_socket.send(json.dumps({"action": "create_article", "data": article}).encode('utf-8'))
                        response = client_socket.recv(1024).decode('utf-8')
                        response_data = json.loads(response)

                        if response_data.get("message") == "Article created successfully!":
                            print("Your article is being posted...")
                        else:
                            print("Failed to post article...")
                            print(response_data)
                        
                        input("\nPress any key to continue...")
                    case "p" | "profile":
                        view_profile(self.current_user, self.current_user_id, client_socket)
                    case "q" | "search":
                        keyword = search_article()
                        client_socket.send(json.dumps({"action": "search_article", "data": keyword}).encode('utf-8'))
                        response = client_socket.recv(4096).decode('utf-8')
                        response_data = json.loads(response)
                            
                        if "articles" in response_data:
                            print("\nSearch Results:")
                            if not response_data["articles"]:
                                print("No articles found for the given keyword.")
                            else:
                                for idx, article in enumerate(response_data["articles"], 1):
                                    print(f"[{idx}] {article['title']} by {article['author']} {article['created_at']}")

                                while True:
                                    try:
                                        print("\nEnter the number to view an article or '0' to go back:")
                                        selection = int(input(f"[{self.current_user}] >>>").strip())
                                        
                                        if selection == 0:
                                            print("Returning to the previous menu...")
                                            break
                                        
                                        if 1 <= selection <= len(response_data["articles"]):
                                            selected_article = response_data["articles"][selection - 1]
                                            view_article(selected_article["article_id"], self.current_user, self.current_user_id, client_socket)
                                            break
                                        else:
                                            print(f"Invalid choice. Please select a number between 0 and {len(response_data['articles'])}.")
                                    except ValueError:
                                        print("Invalid input. Please enter a number.")
                        else:
                            print(response_data)
                        
                        input("\nPress any key to continue...")
                    case "z" | "previous":
                        if current_page > 1:
                            current_page -= 1
                        else:
                            print("You are on the first page.")
                            input("\nPress any key to continue...")
                    case "x" | "next":
                        if current_page < total_pages:
                            current_page += 1
                        else:
                            print("You are on the last page.")
                            input("\nPress any key to continue...")
                    case "v" | "view_a": 
                        if self.current_user_role == "Admin":
                            view_report_articles(client_socket, self.current_user)
                        else:
                            input("\nAdmin role required."
                                  "\nPress any key to continue...")
                    case "m" | "manage":
                        if self.current_user_role == "Admin":
                            manage_user(client_socket, self.current_user)
                        else:
                            input("\nAdmin role required."
                                  "\nPress any key to continue...")
                    case "w" | "view_c":
                        if self.current_user_role == "Admin":
                            view_report_comments(client_socket, self.current_user)
                        else:
                            input("\nAdmin role required."
                                  "\nPress any key to continue...")
                    case _ if command.isdigit() and 1 <= int(command) <= len(articles) + (current_page - 1) * PAGE_SIZE:
                        article_idx = int(command) - 1 - (current_page - 1) * PAGE_SIZE
                        selected_article_id = articles[article_idx]["article_id"]
                        view_article(selected_article_id, self.current_user, self.current_user_id, client_socket)
                    case _:
                        print("Invalid input. Please try again.")
                        input("\nPress any key to continue...")
                        
if __name__ == "__main__":
    client = TCPClient()
    client.start()
