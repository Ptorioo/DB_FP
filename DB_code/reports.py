from init import *

# Function to insert report data for articles or comments
def insert_reports():
    conn = connect_to_postgres()
    cursor = conn.cursor()

    try:
        # 1. Get all user_ids who are not authors and are not followers of the target
        cursor.execute("SELECT user_id FROM USERS")
        all_user_ids = [user_id[0] for user_id in cursor.fetchall()]

        # Get all comments and articles to potentially report
        cursor.execute("SELECT comment_id, owner_id, article_id FROM COMMENTS")
        comments = cursor.fetchall()

        cursor.execute("SELECT article_id, author_id FROM ARTICLES")
        articles = cursor.fetchall()

        # 2. Randomly choose report count (100 to 500 reports)
        num_reports = random.randint(100, 500)
        for _ in range(num_reports):
            # Randomly choose between reporting an article or a comment
            report_type = random.choice(['article', 'comment'])

            if report_type == 'article':
                # Choose a random article
                target_article = random.choice(articles)
                target_article_id = target_article[0]
                target_author_id = target_article[1]

                cursor.execute("SELECT follower_id FROM USER_FOLLOWERS WHERE followee_id = %s", (target_author_id,))
                followers = [follower[0] for follower in cursor.fetchall()]

                # Generate random report reason
                reason = faker.paragraph(nb_sentences=1)

                # Choose a random reporter who is not the author or a follower of the article's author
                reporter_id = random.choice([user_id for user_id in all_user_ids if user_id != target_author_id and user_id not in followers])

                # Insert report for article into REPORT_A table
                cursor.execute("""
                    INSERT INTO REPORT_A (reporter_id, target_article_id, reason)
                    VALUES (%s, %s, %s)
                """, (reporter_id, target_article_id, reason))
                conn.commit()

            elif report_type == 'comment':
                # Choose a random comment
                target_comment = random.choice(comments)
                target_comment_id = target_comment[0]
                target_comment_owner_id = target_comment[1]

                cursor.execute("SELECT follower_id FROM USER_FOLLOWERS WHERE followee_id = %s", (target_author_id,))
                followers = [follower[0] for follower in cursor.fetchall()]

                # Generate random report reason
                reason = faker.paragraph(nb_sentences=1)

                # Choose a random reporter who is not the comment's owner
                reporter_id = random.choice([user_id for user_id in all_user_ids if user_id != target_comment_owner_id])

                # Insert report for comment into REPORT_C table
                cursor.execute("""
                    INSERT INTO REPORT_C (reporter_id, target_comment_id, reason)
                    VALUES (%s, %s, %s)
                """, (reporter_id, target_comment_id, reason))
                conn.commit()
                
        print(f"Successfully inserted {num_reports} reports.")

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

# Main entry point
if __name__ == "__main__":
    insert_reports()
