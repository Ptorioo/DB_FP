def create_comment(article, current_user_id):
    comment_content = input("Enter your comment: ").strip()
    if comment_content:
        comment_data = {
                "article_id": article["article_id"],
                "owner_id": current_user_id,
                "content": comment_content
        }

        return comment_data
    else:
        print("Comment cannot be empty.")
        return None