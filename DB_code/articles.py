from init import *

def insert_articles():
    conn = connect_to_postgres()
    cursor = conn.cursor()

    fake = Faker()

    try:
        # 1. Get all user_ids from USERS table to know who can write articles
        cursor.execute("SELECT user_id FROM USERS")
        user_ids = [user_id[0] for user_id in cursor.fetchall()]

        size = random.randint(1000, 5000)
        selected_user_ids = random.sample(user_ids, size)        

        for user_id in selected_user_ids:
            # Choose a random number of articles to create for each user (e.g., 1 to 3 articles per user)
            num_articles = random.randint(1, 3)

            for _ in range(num_articles):
                title = fake.paragraph(nb_sentences=1)  # Random article title
                content = fake.paragraph(nb_sentences=7)  # Random article content

                cursor.execute("""INSERT INTO ARTICLES (author_id, title, content)
                                  VALUES (%s, %s, %s)""", ((user_id, title, content)))

                # Commit changes
                conn.commit()
        # print(f"Successfully inserted {len(articles_data)} article records.")

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

# Main entry point
if __name__ == "__main__":
    insert_articles()
