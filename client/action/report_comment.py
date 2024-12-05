import os

def report_comment(comment, current_user_id):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"Reporting Comment by {comment['author']}:")
    print(f"'{comment['content']}'\n")

    reason = input("Enter the reason for reporting this comment: ").strip()
    if reason:
        report = {"reporter_id": current_user_id, "target_comment_id": comment["comment_id"], "reason": reason}
        print("Your report has been submitted. Thank you!")
    else:
        print("Report reason cannot be empty. Report not submitted.")
    input("\nPress any key to continue...")

    return report