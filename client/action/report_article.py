import os

def report_article(article, current_user_id):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"Reporting Article: {article['title']}")
    print(f"Created on: {article['created_at']}")
    print(f"Author: {article['author']}\n")

    reason = input("Enter the reason for reporting this article: ").strip()
    if reason:
        report = {"reporter_id": current_user_id, "target_article_id": article["article_id"], "reason": reason}
    else:
        print("Report reason cannot be empty. Report not submitted.")
    input("\nPress any key to continue...")

    return report