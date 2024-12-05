import os
import datetime
import json
from action.report_article import *
from action.report_comment import *

def view_article(article, current_user, current_user_id, client_socket):
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"Title: {article['title']}")
        print(f"Created on: {article['created_at']}")
        print(f"Author: {article['author']}\n")
        print(f"{article['content']}\n")
        print("Comments:")
        for idx, comment in enumerate(article["comments"], start=1):
            print(f"[{idx}] {comment['author']} (at {comment['created_at']}): {comment['content']}")

        print("\nR [REPORT] Report this article")
        print("C [COMMENT] Create a comment")
        print("0 [EXIT] Go back")
        command = input(f"[{current_user}] >>>").strip().lower()

        match command:
            case "c" | "comment":
                comment_content = input("Enter your comment: ").strip()
                if comment_content:
                    comment_data = {
                            "article_id": article["article_id"],
                            "owner_id": current_user_id,
                            "content": comment_content
                    }

                    client_socket.send(json.dumps({"action": "create_comment", "data": comment_data}).encode('utf-8'))
                    response = client_socket.recv(1024).decode('utf-8')
                    response_data = json.loads(response)

                    if response_data.get("message") == "Comment created successfully!":
                        print("Your comment is being posted...")
                    else:
                        print("Failed to post comment...")
                input("\nPress any key to continue...")
            case "r" | "report":
                report = report_article(article, current_user_id)

                client_socket.send(json.dumps({"action": "report_article", "data": report}).encode('utf-8'))
                response = client_socket.recv(1024).decode('utf-8')
                response_data = json.loads(response)

                if response_data.get("message") == "Article reported successfully!":
                    print("Article is being reported...")
                else:
                    print("Failed to report article...")
                input("\nPress any key to continue...")

            case _ if command.isdigit() and 1 <= int(command) <= len(article["comments"]):
                comment_idx = int(command) - 1
                selected_comment = article["comments"][comment_idx]
                print(f"\nSelected Comment by {selected_comment['author']}:")
                print(f"'{selected_comment['content']}'\n")
                print("\nR [REPORT] Report this comment")
                print("0 [EXIT] Go back")

                comment_action = input(f"[{current_user}] >>>").strip().lower()
                if comment_action == "r" or comment_action == "report":
                    report = report_comment(selected_comment, current_user_id)

                    client_socket.send(json.dumps({"action": "report_comment", "data": report}).encode('utf-8'))
                    response = client_socket.recv(1024).decode('utf-8')
                    response_data = json.loads(response)

                    print(response_data)

                    if response_data.get("message") == "Comment reported successfully!":
                        print("Comment is being reported...")
                    else:
                        print("Failed to report comment...")
                    input("\nPress any key to continue...")
                elif comment_action == "0" or comment_action == "exit":
                    break
                else:
                    print("Invalid input. Please try again.")
                    input("\nPress any key to continue...")

            case "0" | "exit":
                break