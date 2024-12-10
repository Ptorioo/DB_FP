from init import *

def archive_random_articles():
    conn = connect_to_postgres()
    cursor = conn.cursor()

    try:
        # 1. Get the total number of articles
        cursor.execute("SELECT article_id FROM ARTICLES WHERE status = 'active'")
        articles = cursor.fetchall()

        # 2. Randomly select between 500 and 1000 articles
        num_articles_to_archive = random.randint(500, 1000)
        selected_articles = random.sample(articles, num_articles_to_archive)

        # 3. Move the selected articles to ARCHIVED_ARTICLES table and update their status
        for article in selected_articles:
            article_id = article[0]
            # Fetch the article details
            cursor.execute("SELECT article_id, author_id, title, content, created_at FROM ARTICLES WHERE article_id = %s", (article_id,))
            article_data = cursor.fetchone()

            # Insert the article into ARCHIVED_ARTICLES table
            cursor.execute("""
                INSERT INTO ARCHIVED_ARTICLES (article_id, author_id, title, content, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, article_data)

            # Update the status of the article in ARTICLES table
            cursor.execute("""
                UPDATE ARTICLES
                SET status = 'archived'
                WHERE article_id = %s
            """, (article_id,))

        # Commit the transaction
        conn.commit()

        print(f"Successfully archived {num_articles_to_archive} articles.")

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

# Main entry point
if __name__ == "__main__":
    archive_random_articles()
