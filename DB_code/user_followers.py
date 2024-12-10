from init import *

def insert_user_followers():
    conn = connect_to_postgres()
    cursor = conn.cursor()

    try:
        # 1. Get all user_ids from USERS table
        cursor.execute("SELECT user_id FROM USERS")
        user_ids = [user_id[0] for user_id in cursor.fetchall()]

        # 2. For each user, randomly choose followers (ensure follower is not the same as followee)
        followers_data = []

        for followee_id in user_ids:
            # Choose a random number of followers (let's say each user follows 1 to 5 others)
            num_followers = random.randint(1, 5)
            followers = random.sample([user_id for user_id in user_ids if user_id != followee_id], num_followers)

            for follower_id in followers:
                cursor.execute("""
                    INSERT INTO USER_FOLLOWERS (follower_id, followee_id)
                    VALUES (%s, %s)
                """, (follower_id, followee_id))
        # 3. Insert the follower data into USER_FOLLOWERS table
        
        
        # Commit changes
                conn.commit()
        #print(f"Successfully inserted {len(followers_data)} user follower records.")

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

# Main entry point
if __name__ == "__main__":
    insert_user_followers()
