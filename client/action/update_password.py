def update_password():
    new_password = input("Enter a new password: ").strip()
    if new_password:
        return new_password
    else:
        print("Password cannot be empty.")