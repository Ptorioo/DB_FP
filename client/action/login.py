def login_user():
    username = input("Enter your username: ").strip()

    password = input("Enter your password: ").strip()

    return {"username": username, "password": password}