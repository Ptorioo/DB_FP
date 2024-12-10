import os
import json

def manage_user(client_socket, current_user):
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"Welcome, {current_user}. User Management Portal\n")

        user_id = input("Enter the User ID to view details (or 0 to exit): ").strip()
        if user_id == "0":
            return

        if not user_id.isdigit():
            print("Invalid User ID. Please try again.")
            input("\nPress any key to continue...")
            continue

        # 請求伺服器端查詢指定用戶
        client_socket.send(json.dumps({"action": "review_users", "data": {"user_id": int(user_id)}}).encode('utf-8'))
        response = client_socket.recv(8192).decode('utf-8')
        response_data = json.loads(response)

        if not response_data or "message" in response_data:
            print(f"Failed to retrieve user information. Error: {response_data.get('message', 'Unknown error')}")
            input("\nPress any key to continue...")
            continue

        # 確保獲取到 user_info 列表
        user_info = response_data.get("user_info", [])
        if not user_info:
            print("No user found with the given ID.")
            input("\nPress any key to continue...")
            continue

        # 假設返回的 user_info 列表中只會有一個用戶，直接取第一個
        user = user_info[0]
        print(f"Managing User ID: {user['user_id']}\n")
        print(f"Username: {user['username']}")
        print(f"Email: {user['email']}")
        print(f"Status: {user['status']}")
        print(f"Report Count: {user['report_count']}\n")

        command = input(
            "\n0 [Exit] Go back\n"
            "U [Update] Update user status\n"
            "R [Remove] Remove user\n"
            "Select Option: ").strip().lower()

        match command:
            case "0" | "exit":
                break
            case "u" | "update":
                update_user_status(client_socket, user)
            case "r" | "remove":
                remove_user(client_socket, user)
            case _:
                print("Invalid input. Please try again.")
                input("\nPress any key to continue...")

def update_user_status(client_socket, user):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"Updating Status for User ID: {user['user_id']}\n")
    print(f"Current Status: {user['status']}\n")
    print("Available Status Options: muted, active, banned")

    new_status = input(
        "\nA [Active] Activate this user\n"
        "B [Banned] Ban this user\n"
        "M [Muted] Mute this user\n"
        "Select Option: ").strip().lower()

    match new_status:
        case "a" | "active":
            client_socket.send(json.dumps({
                "action": "update_user_status",
                "data": {
                    "user_id": user["user_id"],
                    "status": "active"
                }
            }).encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            response_data = json.loads(response)
        
            if response_data.get("message") == "Update Successful!":
                print("User status updated successfully!")
            else:
                print(f"Failed to update status. Error: {response_data.get('message', 'Unknown error')}")
            input("\nPress any key to continue...")
        case "b" | "banned":
            client_socket.send(json.dumps({
                "action": "update_user_status",
                "data": {
                    "user_id": user["user_id"],
                    "status": "banned"
                }
            }).encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            response_data = json.loads(response)
        
            if response_data.get("message") == "Update Successful!":
                print("User status updated successfully!")
            else:
                print(f"Failed to update status. Error: {response_data.get('message', 'Unknown error')}")
            input("\nPress any key to continue...")
        case "m" | "muted":
            client_socket.send(json.dumps({
                "action": "update_user_status",
                "data": {
                    "user_id": user["user_id"],
                    "status": "muted"
                }
            }).encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            response_data = json.loads(response)
        
            if response_data.get("message") == "Update Successful!":
                print("User status updated successfully!")
            else:
                print(f"Failed to update status. Error: {response_data.get('message', 'Unknown error')}")
            input("\nPress any key to continue...")
        case _:
          print("Invalid status. Please try again.")
          input("\nPress any key to continue...")
          return

def remove_user(client_socket, user):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"Removing User ID: {user['user_id']}\n")
    confirm = input("\nY [Yes] Remove this user\n"
                    "N [No] Do not remove this user\n"
                    "Select Option: ").strip().lower()

    match confirm:
        case "y" | "yes":
            client_socket.send(json.dumps({
                "action": "remove_user",
                "data": {
                    "user_id": user["user_id"]
                }
            }).encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            response_data = json.loads(response)

            if response_data.get("message") == "Delete successful!":
                print("User removed successfully!")
            else:
                print(f"Failed to remove user. Error: {response_data.get('message', 'Unknown error')}")
            input("\nPress any key to continue...")
        case _:
            print("User removal canceled.")
            input("\nPress any key to continue...")
            return

      
