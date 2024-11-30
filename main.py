import os
import re
from datetime import datetime

users = {}
articles = []

PAGE_SIZE = 9

def pause():
    input("\nPress any key to continue...")

def report_article(article, current_user):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"Reporting Article: {article['title']}")
    print(f"Created on: {article['created_time']}")
    print(f"Author: {article['author']}\n")
    print(f"{article['content']}\n")

    reason = input("Enter the reason for reporting this article: ").strip()
    if reason:
        article["reports"].append({"author": current_user, "reason": reason, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        print("Your report has been submitted. Thank you!")
    else:
        print("Report reason cannot be empty. Report not submitted.")
    pause()

def report_comment(comment, article, current_user):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"Reporting Comment by {comment['author']}:")
    print(f"'{comment['content']}'\n")

    reason = input("Enter the reason for reporting this comment: ").strip()
    if reason:
        comment["reports"].append({"author": current_user, "reason": reason, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        print("Your report has been submitted. Thank you!")
    else:
        print("Report reason cannot be empty. Report not submitted.")
    pause()

def register_user():
    username = input("Enter a username: ").strip()
    if username in users:
        print("Username already exists. Please try a different one.")
        pause()
        return

    email = input("Enter your email: ").strip()
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_pattern, email):
        print("Invalid email format. Please try again.")
        pause()
        return

    password = input("Enter a password: ").strip()
    if not username or not password:
        print("Username and password cannot be empty.")
        pause()
        return

    users[username] = {"email": email, "password": password}
    print(f"User '{username}' registered successfully with email '{email}'!")
    pause()

def login_user():
    username = input("Enter your username: ").strip()
    if username not in users:
        print("Username not found. Please register first.")
        pause()
        return None

    password = input("Enter your password: ").strip()
    if users[username]["password"] == password:
        print(f"Welcome back, {username}!")
        print(f"Your registered email: {users[username]['email']}")
        pause()
        return username
    else:
        print("Incorrect password. Please try again.")
        pause()
        return None

def create_article(current_user):
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Creating a New Article")

    title = input("Enter the article title: ").strip()
    content = input("Enter the article content: ").strip()

    if not title or not content:
        print("Title and content cannot be empty.")
        pause()
        return

    new_article = {
        "title": title,
        "created_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "content": content,
        "author": current_user,
        "comments": [],
        "reports": []
    }
    articles.append(new_article)
    print(f"New article '{title}' created successfully!")
    pause()

def display_articles(page):
    os.system('cls' if os.name == 'nt' else 'clear')
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    articles_to_display = articles[start:end]

    print("*****Welcome*****")
    for idx, article in enumerate(articles_to_display, start=1):
        print(f"{idx}. {article['title']} (by {article['author']}) {article['created_time']}")

    print("\n0 [LOGOUT] Log out from the platform")
    print("C [CREATE] Create an article")
    print("Z [PREV] Previous page")
    print("X [NEXT] Next page")

def view_article(article, current_user):
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"Title: {article['title']}")
        print(f"Created on: {article['created_time']}")
        print(f"Author: {article['author']}\n")
        print(f"{article['content']}\n")
        print("Comments:")
        for idx, comment in enumerate(article["comments"], start=1):
            print(f"[{idx}] {comment['author']} (at {comment['created_time']}): {comment['content']}")

        print("\nOptions:")
        print("R [REPORT] Report the article")
        print("C [COMMENT] Create a comment")
        print("0 [EXIT] Go back to menu")
        user_input = input("\n>>> ").strip().lower()

        match user_input:
            case "r" | "report":
                report_article(article, current_user)
            case "c" | "comment":
                comment_content = input("Enter your comment: ").strip()
                if comment_content:
                    
                    article["comments"].append({
                        "author": current_user, 
                        "content": comment_content, 
                        "reports": [], 
                        "created_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    print("Your comment has been added.")
                else:
                    print("Comment cannot be empty.")
                pause()
            case "0" | "exit":
                break
            case _ if user_input.isdigit() and 1 <= int(user_input) <= len(article["comments"]):
                comment_idx = int(user_input) - 1
                selected_comment = article["comments"][comment_idx]
                print(f"\nSelected Comment by {selected_comment['author']}:")
                print(f"'{selected_comment['content']}'\n")
                print("Options:")
                print("R [REPORT] Report this comment")
                print("0 [EXIT] Go back to article")
                comment_action = input("\n>>> ").strip().lower()
                if comment_action == "r" or comment_action == "report":
                    report_comment(selected_comment, article, current_user)
                elif comment_action == "0" or comment_action == "exit":
                    break
                else:
                    print("Invalid input. Please try again.")
                    pause()

def main():
    current_user = None
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        user_input = input(
            "\n*****Please select a method to continue*****\n"
            "1 [REGISTER] Register a user\n"
            "2 [LOGIN] Log in to the platform\n"
            "3 [EXIT] Exit from the platform\n"
            ">>> "
        ).strip().lower()

        match user_input:
            case "3" | "exit":
                print("See you later!")
                break
            case "1" | "register":
                register_user()
            case "2" | "login":
                current_user = login_user()
                if current_user:
                    break
            case _:
                print("Invalid input. Please try again.")
                pause()

    page = 0
    while current_user:
        display_articles(page)
        user_input = input(
            ">>> "
        ).strip().lower()

        match user_input:
            case "0" | "logout":
                print("Logging out...")
                current_user = None
                pause()
            case "c" | "create":
                create_article(current_user)
            case "z" | "prev":
                if page > 0:
                    page -= 1
                else:
                    print("Already on the first page.")
                    pause()
            case "x" | "next":
                if (page + 1) * PAGE_SIZE < len(articles):
                    page += 1
                else:
                    print("Already on the last page.")
                    pause()
            case _ if user_input.isdigit() and 1 <= int(user_input) <= len(articles):
                article_idx = int(user_input) - 1
                selected_article = articles[article_idx]
                view_article(selected_article, current_user)
            case _:
                print("Invalid input. Please try again.")
                pause()

if __name__ == "__main__":
    main()
