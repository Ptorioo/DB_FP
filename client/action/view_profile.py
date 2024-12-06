import os
import json

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
            "3 [ACTIVITY] View activity\n"
            f"[{current_user}] >>>").strip().lower()
        
        match command:
            case "0" | "exit":
                break
            case _:
                print("Invalid input. Please try again.")
                input("\nPress any key to continue...")