import psycopg2
import random
import string

# PostgreSQL DB connection parameters
db_password = ""
DB_CONFIG = {
    'dbname': 'DB_FP',
    'user': 'postgres',
    'host': 'localhost',
    'password': db_password
}

# Function to connect to PostgreSQL database
def connect_to_postgres():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("Connected to PostgreSQL!")
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        raise

# Function to insert data into USER_FOLLOWERS table
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
                followers_data.append((follower_id, followee_id))

        # 3. Insert the follower data into USER_FOLLOWERS table
        cursor.executemany("""
            INSERT INTO USER_FOLLOWERS (follower_id, followee_id)
            VALUES (%s, %s)
        """, followers_data)
        
        # Commit changes
        conn.commit()
        print(f"Successfully inserted {len(followers_data)} user follower records.")

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

# Main entry point
if __name__ == "__main__":
    insert_user_followers()
