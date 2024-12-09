import os
import json

def view_report_comments(client_socket, current_user):
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"Welcome, {current_user}. Reviewing pending reported comments...\n")

        # 請求伺服器上的舉報資料
        client_socket.send(json.dumps({"action": "review_comment_report"}).encode('utf-8'))
        response = client_socket.recv(8192).decode('utf-8')
        response_data = json.loads(response)

        # 檢查伺服器回應
        if "report_comments" not in response_data:
            print("Failed to retrieve reports.")
            print(f"Error: {response_data.get('message', 'Unknown error')}")
            input("\nPress any key to continue...")
            return

        reports = response_data["report_comments"]
        if not reports:
            print("No pending reports available.")
            input("\nPress any key to continue...")
            return

        # 列出舉報
        for idx, report in enumerate(reports, start=1):
            print(f"[{idx}] Report ID: {report['report_comment_id']}")
            print(f"    Reporter ID: {report['reporter_id']}")
            print(f"    Target Comment ID: {report['target_comment_id']}")
            print(f"    Reason: {report['reason']}")
            print(f"    Created At: {report['created_at']}\n")

        # 提供選擇
        print("\nOptions:")
        print("0 [Exit] Go back")
        selected_idx = input("Select a report by number to view details: ").strip().lower()

        if selected_idx == "0" or selected_idx == "exit":
            return
        elif selected_idx.isdigit() and 1 <= int(selected_idx) <= len(reports):
            selected_report = reports[int(selected_idx) - 1]

            # 查看特定舉報的詳細內容
            view_report_c_details(client_socket, selected_report)
        else:
            print("Invalid selection.")
            input("\nPress any key to continue...")

def view_report_c_details(client_socket, report):
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"Viewing Report ID: {report['report_comment_id']}\n")
        print(f"Reporter ID: {report['reporter_id']}")
        print(f"Target Comment ID: {report['target_comment_id']}")
        print(f"Reason: {report['reason']}")
        print(f"Created At: {report['created_at']}")
        print(f"\nComment Content: {report['comment_content']}\n")

        print("Options:")
        print("0 [Exit] Go back (Mark as Reviewed)")
        print("D [Delete] Delete this comment")

        action = input("Select an option: ").strip().lower()

        if action == "0" or action == "exit":
            # 更新舉報狀態為 reviewed
            client_socket.send(json.dumps({
                "action": "update_comment_report",
                "data": {
                    "report_comment_id": report["report_comment_id"],
                    "status": "reviewed"
                }
            }).encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            response_data = json.loads(response)

            if response_data.get("message") == "Report update!":
                print("Report marked as reviewed.")
            else:
                print(f"Failed to update report. Error: {response_data.get('message', 'Unknown error')}")
            input("\nPress any key to continue...")
            break

        elif action == "d" or action == "delete":
            # 刪除留言
            client_socket.send(json.dumps({
                "action": "delete_comment",
                "data": {
                    "comment_id": report["target_comment_id"]
                }
            }).encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            response_data = json.loads(response)

            if response_data.get("message") == "Comment deleted successfully!":
                print("Comment deleted successfully.")
                
                # 更新舉報狀態為 reviewed
                client_socket.send(json.dumps({
                    "action": "update_comment_report",
                    "data": {
                        "report_comment_id": report["report_comment_id"],
                        "status": "reviewed"
                    }
                }).encode('utf-8'))
                response = client_socket.recv(1024).decode('utf-8')
                response_data = json.loads(response)

                if response_data.get("message") == "Report update!":
                    print("Report marked as reviewed.")
                else:
                    print(f"Failed to update report. Error: {response_data.get('message', 'Unknown error')}")
            else:
                print(f"Failed to delete comment. Error: {response_data.get('message', 'Unknown error')}")

            input("\nPress any key to continue...")
            break

        else:
            print("Invalid input. Please try again.")
            input("\nPress any key to continue...")
