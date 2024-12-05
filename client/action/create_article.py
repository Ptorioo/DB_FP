import os
import datetime

def create_article(current_user_id):
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Creating a New Article")

    title = input("Enter the article title: ").strip()
    content = input("Enter the article content: ").strip()

    if not title or not content:
        print("Title and content cannot be empty.")
        input("\nPress any key to continue...")
        return

    new_article = {
        "author_id": current_user_id,
        "title": title,
        "content": content
    }
    return new_article