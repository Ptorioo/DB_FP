import re

def register_user():
    username = input("Enter a username: ").strip()

    email = input("Enter your email: ").strip()
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_pattern, email):
        print("Invalid email format. Please try again.")
        input("\nPress any key to continue...")
        return

    password = input("Enter a password: ").strip()
    if not username or not password:
        print("Username and password cannot be empty.")
        input("\nPress any key to continue...")
        return

    result = {"username": username, "email": email, "password": password}
    return result