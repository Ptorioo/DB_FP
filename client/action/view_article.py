import os
import datetime
import json

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

        print("\nR [REPORT] Report the article")
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
            case "0" | "exit":
                break
'''
        match command:
            case "r" | "report":
                report_article(article, current_user)
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
'''