import os
import json

from action.update_email import *
from action.update_password import *

def view_profile(current_user, current_user_id, client_socket):
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"*****Profile of {current_user}*****")

        print("★ Favorited Articles ★\n")
        client_socket.send(json.dumps({"action": "get_favorites", "data": current_user_id}).encode('utf-8'))
        response = client_socket.recv(4096).decode('utf-8')
        response_data = json.loads(response)

        if favorites := response_data.get("favorites"):
            for i, fav in enumerate(favorites, start=1):
                print(f"{i}. {fav['title']} by {fav['author']}")
                print(f"   - Published on: {fav['created_at']}\n")
        else:
            print("You have no favorite articles yet.\n")

        print("★ Articles from Users You Follow ★\n")
        client_socket.send(json.dumps({"action": "get_followings", "data": current_user_id}).encode('utf-8'))
        response = client_socket.recv(4096).decode('utf-8')
        response_data = json.loads(response)

        if followings := response_data.get("followings"):
            for i, article in enumerate(followings, start=1):
                print(f"{i}. {article['title']} by {article['author']}")
                print(f"   - Published on: {article['created_at']}\n")
        else:
            print("No articles found from the users you follow.\n")

        command = input(
            "\n0 [EXIT] Return to menu\n"
            "1 [EMAIL] Change email\n"
            "2 [PWD] Change password\n"
            "3 [ARTICLE] View your articles\n"
            "4 [ARCHIVE] View archived articles\n"
            f"[{current_user}] >>>").strip().lower()
        
        match command:
            case "0" | "exit":
                break
            case "1" | "email":
                new_email = update_email()

                client_socket.send(json.dumps({"action": "update_email", "data": {"user_id": current_user_id, "new_email": new_email}}).encode('utf-8'))
                response = client_socket.recv(1024).decode('utf-8')
                response_data = json.loads(response)

                if response_data.get("message") == "Email updated!":
                    print("Email updated!")
                else:
                    print("Email update failed.")

                input("\nPress any key to continue...")
            case "2" | "pwd":
                new_password = update_password()

                client_socket.send(json.dumps({"action": "update_password", "data": {"user_id": current_user_id, "new_password": new_password}}).encode('utf-8'))
                response = client_socket.recv(1024).decode('utf-8')
                response_data = json.loads(response)

                if response_data.get("message") == "Password updated!":
                    print("Password updated!")
                else:
                    print(response_data)
                    print("Password update failed.")

                input("\nPress any key to continue...")
            case "3" | "article":
                client_socket.send(json.dumps({"action": "get_user_article", "data": current_user_id}).encode('utf-8'))
                response = client_socket.recv(4096).decode('utf-8')
                response_data = json.loads(response)

                if articles := response_data.get("articles"):
                    for i, article in enumerate(articles, start=1):
                        print(f"[{i}] {article['title']} - at {article['created_at']}\n")
                    
                    command = input(
                        "Select index to archive articles, or press 0 to exit: "
                        )
                    
                    match command:
                        case "0":
                            pass
                        case _ if command.isdigit() and int(command) != 0:
                            client_socket.send(json.dumps({"action": "archive_article", "data": {"user_id": current_user_id, "article_id": articles[int(command) - 1]["article_id"]}}).encode('utf-8'))
                            response = client_socket.recv(4096).decode('utf-8')
                            response_data = json.loads(response)

                            print(response_data.get("message"))
                        case _:
                            print("Invalid input. Please try again.")
                            pass
                else:
                    print("You have no public articles yet.\n")
                
                input("\nPress any key to continue...")
            case "4" | "archive":
                client_socket.send(json.dumps({"action": "get_user_archive", "data": current_user_id}).encode('utf-8'))
                response = client_socket.recv(4096).decode('utf-8')
                response_data = json.loads(response)

                if articles := response_data.get("articles"):
                    for i, article in enumerate(articles, start=1):
                        print(f"[{i}] {article['title']} - at {article['created_at']}\n")
                    
                    command = input(
                        "Select index to unarchive articles, or press 0 to exit: "
                        )
                    
                    match command:
                        case "0":
                            pass
                        case _ if command.isdigit() and int(command) != 0:
                            client_socket.send(json.dumps({"action": "unarchive_article", "data": {"user_id": current_user_id, "article_id": articles[int(command) - 1]["article_id"]}}).encode('utf-8'))
                            response = client_socket.recv(4096).decode('utf-8')
                            response_data = json.loads(response)

                            print(response_data.get("message"))
                        case _:
                            print("Invalid input. Please try again.")
                            pass
                else:
                    print("You have no public articles yet.\n")
                
                input("\nPress any key to continue...")
            case _:
                print("Invalid input. Please try again.")
                input("\nPress any key to continue...")