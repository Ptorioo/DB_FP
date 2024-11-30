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
        print(f"[{idx}] {article['title']} (by {article['author']}) {article['created_time']}")

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

        print("\nR [REPORT] Report the article")
        print("C [COMMENT] Create a comment")
        print("0 [EXIT] Go back")
        user_input = input(f"[{current_user}] >>>").strip().lower()

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
                print("\nR [REPORT] Report this comment")
                print("0 [EXIT] Go back")
                comment_action = input(f"[{current_user}] >>>").strip().lower()
                if comment_action == "r" or comment_action == "report":
                    report_comment(selected_comment, article, current_user)
                elif comment_action == "0" or comment_action == "exit":
                    break
                else:
                    print("Invalid input. Please try again.")
                    pause()

def view_profile(current_user):
    def paginate_items(items, page):
        start = page * PAGE_SIZE
        end = start + PAGE_SIZE
        return items[start:end], start

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        user_data = users[current_user]
        print(f"Profile of {current_user}")
        print(f"Email: {user_data['email']}")

        user_input = input(
            "\n0 [EXIT] Return to menu\n"
            "1 [EMAIL] Change email\n"
            "2 [PWD] Change password\n"
            "3 [CMT] View comment history\n"
            "4 [POST] View post history\n"
            f"[{current_user}] >>>").strip().lower()

        match user_input:
            case "0" | "exit":
                break
            case "1" | "email":
                new_email = input("Enter a new email: ").strip()
                email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
                if re.match(email_pattern, new_email):
                    users[current_user]["email"] = new_email
                    print("Email updated successfully!")
                else:
                    print("Invalid email format. Please try again.")
                pause()
            case "2" | "pwd":
                new_password = input("Enter a new password: ").strip()
                if new_password:
                    users[current_user]["password"] = new_password
                    print("Password updated successfully!")
                else:
                    print("Password cannot be empty.")
                pause()
            case "3" | "cmt":
                comments = [
                    {"article": article, "comment": comment, "index": idx}
                    for article in articles
                    for idx, comment in enumerate(article["comments"], start=1)
                    if comment["author"] == current_user
                ]

                page = 0
                while True:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    if not comments:
                        print("No comments found.")
                        pause()
                        break

                    paginated_comments, start_idx = paginate_items(comments, page)
                    print(f"Comment History for {current_user} (Page {page + 1}):")
                    for idx, entry in enumerate(paginated_comments, start=start_idx + 1):
                        article_title = entry["article"]["title"]
                        comment_content = entry["comment"]["content"]
                        created_time = entry["comment"]["created_time"]
                        print(f"[{idx}] On '{article_title}': {comment_content} (at {created_time})")

                    user_input = input("\n0 [EXIT] Return to profile\n"
                                       "Z [PREV] Previous page\n"
                                       "X [NEXT] Next page\n"
                                       f"[{current_user}] >>>").strip().lower()

                    if user_input == "0" or user_input == "exit":
                        break
                    elif user_input == "z" or user_input == "prev":
                        if page > 0:
                            page -= 1
                        else:
                            print("Already on the first page.")
                            pause()
                    elif user_input == "x" or user_input == "next":
                        if (page + 1) * PAGE_SIZE < len(comments):
                            page += 1
                        else:
                            print("Already on the last page.")
                            pause()
                    elif user_input.isdigit() and 1 <= int(user_input) <= len(comments):
                        selected_comment = comments[int(user_input) - 1]
                        os.system('cls' if os.name == 'nt' else 'clear')
                        print(f"Redirecting to article '{selected_comment['article']['title']}'...\n")
                        pause()
                        view_article(selected_comment["article"], current_user)
                        break
                    else:
                        print("Invalid input. Please try again.")
                        pause()
            case "4" | "post":
                user_posts = [article for article in articles if article["author"] == current_user]

                page = 0
                while True:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    if not user_posts:
                        print("No posts found.")
                        pause()
                        break

                    paginated_posts, start_idx = paginate_items(user_posts, page)
                    print(f"Post History for {current_user} (Page {page + 1}):")
                    for idx, post in enumerate(paginated_posts, start=start_idx + 1):
                        print(f"[{idx}] '{post['title']}' (created on {post['created_time']})")

                    user_input = input("\n0 [EXIT] Return to profile\n"
                                       "Z [PREV] Previous page\n"
                                       "X [NEXT] Next page\n"
                                       f"[{current_user}] >>>").strip().lower()

                    if user_input == "0" or user_input == "exit":
                        break
                    elif user_input == "z" or user_input == "prev":
                        if page > 0:
                            page -= 1
                        else:
                            print("Already on the first page.")
                            pause()
                    elif user_input == "x" or user_input == "next":
                        if (page + 1) * PAGE_SIZE < len(user_posts):
                            page += 1
                        else:
                            print("Already on the last page.")
                            pause()
                    elif user_input.isdigit() and 1 <= int(user_input) <= len(user_posts):
                        selected_post = user_posts[int(user_input) - 1]
                        os.system('cls' if os.name == 'nt' else 'clear')
                        print(f"Redirecting to article '{selected_post['title']}'...\n")
                        pause()
                        view_article(selected_post, current_user)
                        break
                    else:
                        print("Invalid input. Please try again.")
                        pause()
            case _:
                print("Invalid input. Please try again.")
                pause()

def main():
    current_user = None
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        user_input = input(
            "*****Please select a method to continue*****\n"
            "0 [EXIT] Exit from the platform\n"
            "1 [REGISTER] Register a user\n"
            "2 [LOGIN] Log in to the platform\n"
            ">>>"
        ).strip().lower()

        match user_input:
            case "0" | "exit":
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
            "\n0 [LOGOUT] Log out from the platform\n"
            "C [CREATE] Create an article\n"
            "P [PROFILE] View user profile\n"
            "Z [PREV] Previous page\n"
            "X [NEXT] Next page\n"
            f"[{current_user}] >>>"
        ).strip().lower()

        match user_input:
            case "0" | "logout":
                print("Logging out...")
                current_user = None
                pause()
            case "c" | "create":
                create_article(current_user)
            case "p" | "profile":
                view_profile(current_user)
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
