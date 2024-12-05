import socket
import os
import json
from action.register import *
from action.login import *
from action.view_article import *
from action.create_article import *

SERVER_IP = '127.0.0.1'
SERVER_PORT = 8080

PAGE_SIZE = 9

class TCPClient:
    def __init__(self, host=SERVER_IP, port=SERVER_PORT):
        self.host = host
        self.port = port
        self.current_user = None
        self.current_user_id = None

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
                            break

                        input("\nPress any key to continue...")

                    case _:
                        print("Invalid input. Please try again.")
                        input("\nPress any key to continue...")
                
            while self.current_user:
                os.system('cls' if os.name == 'nt' else 'clear')
                print("*****Welcome*****")

                # WARNING: This method is strongly advised to be improved in the future as loading all articles into buffer is very inefficient and could cause data overflow (by Arthur)
                client_socket.send(json.dumps({"action": "get_articles"}).encode('utf-8'))
                response = client_socket.recv(4096).decode('utf-8')
                response_data = json.loads(response)
                
                for idx, article in enumerate(response_data, start=1):
                    print(f"[{idx}] {article['title']} by {article['author']} {article['created_at']}")

                command = input(
                    "\n0 [LOGOUT] Log out from the platform\n"
                    "C [CREATE] Create an article\n"
                    "P [PROFILE] View user profile\n"
                    f"[{self.current_user}] >>>"
                ).strip().lower()

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
                    case _ if command.isdigit() and 1 <= int(command) <= len(response_data):
                        article_idx = int(command) - 1
                        selected_article_idx = response_data[article_idx]["article_id"]

                        client_socket.send(json.dumps({"action": "get_article", "data": selected_article_idx}).encode('utf-8'))
                        response = client_socket.recv(4096).decode('utf-8')
                        response_data = json.loads(response)

                        view_article(response_data, self.current_user, self.current_user_id, client_socket)
                    case _:
                        print("Invalid input. Please try again.")
                        input("\nPress any key to continue...")
'''
                    case "p" | "profile":
                        view_profile(self.current_user)
'''
if __name__ == "__main__":
    client = TCPClient()
    client.start()
