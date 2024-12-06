import os
import datetime
import json
from action.report_article import *
from action.report_comment import *
from action.create_comment import *

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

        client_socket.send(json.dumps({"action": "is_following", "data": {"user_id": current_user_id, "author_id": article["author_id"]}}).encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        response_data = json.loads(response)
        following = False

        if response_data.get("message") == "User is following.":
            print("F [UNFOLLOW] Unfollow the author")
            following = True
        else:
            print("F [FOLLOW] Follow the author")

        client_socket.send(json.dumps({"action": "is_favorite", "data": {"user_id": current_user_id, "article_id": article["article_id"]}}).encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        response_data = json.loads(response)
        is_favorite = False

        if response_data.get("message") == "User is favoriting.":
            print("S [UNFAVORITE] Unfavorite this article")
            is_favorite = True
        else:
            print("S [FAVORITE] Favorite this article")
        
        print("0 [EXIT] Go back")
        command = input(f"[{current_user}] >>>").strip().lower()

        match command:
            case "c" | "comment":
                comment_data= create_comment(article, current_user_id)
                if comment_data:

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
            case "f" | "follow" | "unfollow":
                if following == True:
                    client_socket.send(json.dumps({"action": "unfollow_user", "data": {"follower_id": current_user_id, "followee_id": article["author_id"]}}).encode('utf-8'))
                    response = client_socket.recv(1024).decode('utf-8')
                    response_data = json.loads(response)

                    if response_data.get("message") == "User is no longer following.":
                        print("Unfollowed successfully!")
                        following = False
                    else:
                        print("Unfollow failed.")
                else:
                    client_socket.send(json.dumps({"action": "follow_user", "data": {"follower_id": current_user_id, "followee_id": article["author_id"]}}).encode('utf-8'))
                    response = client_socket.recv(1024).decode('utf-8')
                    response_data = json.loads(response)

                    if response_data.get("message") == "User is now following.":
                        print("Followed successfully!")
                        following = True
                    else:
                        print("Follow failed.")
                input("\nPress any key to continue...")
            case "s" | "favorite" | "unfavorite":
                if is_favorite == True:
                    client_socket.send(json.dumps({"action": "unfavorite_article", "data": {"user_id": current_user_id, "article_id": article["article_id"]}}).encode('utf-8'))
                    response = client_socket.recv(1024).decode('utf-8')
                    response_data = json.loads(response)

                    if response_data.get("message") == "User is no longer favoriting.":
                        print("Unfavorited successfully!")
                        is_favorite = False
                    else:
                        print("Unfavorite failed.")
                else:
                    client_socket.send(json.dumps({"action": "favorite_article", "data": {"user_id": current_user_id, "article_id": article["article_id"]}}).encode('utf-8'))
                    response = client_socket.recv(1024).decode('utf-8')
                    response_data = json.loads(response)

                    if response_data.get("message") == "User is now favoriting.":
                        print("Favorited successfully!")
                        is_favorite = True
                    else:
                        print(response_data)
                        print("Favorite failed.")
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