import re

def update_email():
    new_email = input("Enter a new email: ").strip()
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if re.match(email_pattern, new_email):
        return new_email
    else:
        print("Invalid email format. Please try again.")