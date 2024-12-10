from init import *

def user_shared_favorites():
    conn = connect_to_postgres()
    cursor = conn.cursor()

    try:
        # 1. 從 ARTICLES 表中選擇所有的文章
        cursor.execute("SELECT article_id, author_id FROM ARTICLES")
        articles = cursor.fetchall()

        # 2. 從 USERS 表中選擇所有的用戶
        cursor.execute("SELECT user_id FROM USERS")
        users = [user_id[0] for user_id in cursor.fetchall()]

        for article_id, author_id in articles:
            # 3. 根據每篇文章設定隨機數量的動作 (5 到 10 個)
            num_actions = random.randint(-10, 20)
            
            if num_actions > 0:
                # 計算從追蹤者和非追蹤者中選擇的動作數量
                num_followers_actions = int(num_actions * 0.8)
                num_non_followers_actions = num_actions - num_followers_actions

                # 4. 從追蹤者中隨機選擇動作
                cursor.execute("SELECT follower_id FROM USER_FOLLOWERS WHERE followee_id = %s", (author_id,))
                followers = [follower[0] for follower in cursor.fetchall()]
                random.shuffle(followers)  # 隨機打亂追蹤者順序

                # 5. 從非追蹤者中隨機選擇動作
                non_followers = [user_id for user_id in users if user_id not in followers]
                random.shuffle(non_followers)  # 隨機打亂非追蹤者順序

                # 6. 記錄追蹤者的動作
                for i in range(min(num_followers_actions, len(followers))):
                    user_id = followers[i]
                    action_type = random.choices([1, 2], weights=(0.5, 0.5))[0]  # 分享與儲存的比例是1:1
                    if action_type == 1:
                        cursor.execute("INSERT INTO USER_SHARED (user_id, article_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (user_id, article_id))
                        conn.commit()
                    else:
                        cursor.execute("INSERT INTO USER_FAVORITES (user_id, article_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (user_id, article_id))
                        conn.commit()

                # 7. 記錄非追蹤者的動作
                for i in range(min(num_non_followers_actions, len(non_followers))):
                    user_id = non_followers[i]
                    action_type = random.choices([1, 2], weights=(0.5, 0.5))[0]  # 分享與儲存的比例是1:1
                    if action_type == 1:
                        cursor.execute("INSERT INTO USER_SHARED (user_id, article_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (user_id, article_id))
                        conn.commit()
                    else:
                        cursor.execute("INSERT INTO USER_FAVORITES (user_id, article_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (user_id, article_id))
                        conn.commit()

                    # 如果非追蹤者選擇分享，則開始追蹤作者
                    if action_type == 1:
                        cursor.execute("INSERT INTO USER_FOLLOWERS (follower_id, followee_id) VALUES (%s, %s)", (user_id, author_id))
                        conn.commit()

        print("User share/favorite actions inserted successfully.")

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

# Main entry point
if __name__ == "__main__":
    user_shared_favorites()
