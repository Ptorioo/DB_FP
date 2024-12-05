import socket
import os
import json
from action.register import register_user
from action.login import login_user

SERVER_IP = '127.0.0.1'
SERVER_PORT = 8080

PAGE_SIZE = 9

class TCPClient:
    def __init__(self, host=SERVER_IP, port=SERVER_PORT):
        self.host = host
        self.port = port
        self.current_user = None

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
                            break

                        input("\nPress any key to continue...")

                    case _:
                        print("Invalid input. Please try again.")
                        input("\nPress any key to continue...")
                
            while self.current_user:
                os.system('cls' if os.name == 'nt' else 'clear')
                print("*****Welcome*****")

                client_socket.send(json.dumps({"action": "get_articles"}).encode('utf-8'))
                response = client_socket.recv(1024).decode('utf-8')
                response_data = json.loads(response)
                
                for idx, article in enumerate(response_data, start=1):
                    print(f"[{idx}] {article['title']} {article['created_at']}")

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
        
'''                    case "c" | "create":
                        create_article(self.current_user)
                    case "p" | "profile":
                        view_profile(self.current_user)
                    case _ if user_input.isdigit() and 1 <= int(user_input) <= len(articles):
                        article_idx = int(user_input) - 1
                        selected_article = articles[article_idx]
                        view_article(selected_article, self.current_user)
                    case _:
                        print("Invalid input. Please try again.")
                        input("\nPress any key to continue...")
            
'''
if __name__ == "__main__":
    client = TCPClient()
    client.start()
