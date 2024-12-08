def view_report_a_details(client_socket, report):
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"Viewing Report ID: {report['report_article_id']}\n")
        print(f"Reporter ID: {report['reporter_id']}")
        print(f"Target Article ID: {report['target_article_id']}")
        print(f"Reason: {report['reason']}")
        print(f"Created At: {report['created_at']}")
        print(f"\nArticle Title: {report['article_title']}")
        print(f"\nArticle Content: {report['article_content']}\n")

        print("Options:")
        print("0 [Exit] Go back (Mark as Reviewed)")
        print("D [Delete] Delete this article")

        command = input("Select an option: ").strip().lower()

        if command == "0" or command == "exit":
            # 更新舉報狀態為 reviewed
            client_socket.send(json.dumps({
                "action": "update_article_report",
                "data": {
                    "report_article_id": report["report_article_id"],
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

        elif command == "d" or command == "delete":
            # 刪除留言
            client_socket.send(json.dumps({
                "action": "delete_article",
                "data": {
                    "article_id": report["target_article_id"]
                }
            }).encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            response_data = json.loads(response)

            if response_data.get("message") == "article deleted successfully!":
                print("article deleted successfully.")
                
                # 更新舉報狀態為 reviewed
                client_socket.send(json.dumps({
                    "action": "update_article_report",
                    "data": {
                        "report_article_id": report["report_article_id"],
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
                print(f"Failed to delete article. Error: {response_data.get('message', 'Unknown error')}")

            input("\nPress any key to continue...")
            break

        else:
            print("Invalid input. Please try again.")
            input("\nPress any key to continue...")
