import psycopg2
import random
import string
from faker import Faker

# Initialize Faker
faker = Faker()

# PostgreSQL DB connection parameters
db_password = "" # fill in your password
DB_CONFIG = {
    'dbname': 'DB_FP',
    'user': 'postgres',
    'host': 'localhost',
    'password': db_password
}

# Number of users to generate
NUM_USERS = 12000

# Function to generate random string (for passwords)
def random_string(length):
    return ''.join(random.choices(string.ascii_letters, k=length))

# Function to connect to PostgreSQL database
def connect_to_postgres():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("Connected to PostgreSQL!")
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        raise

# Ensure unique username by checking against existing usernames in the database
def generate_unique_username(cursor):
    # Generate a random base username (length between 4 to 16)
    base_username = faker.user_name()
    username = base_username
    cursor.execute("SELECT 1 FROM USERS WHERE username = %s", (username,))
    while cursor.fetchone():  # If username exists, regenerate
        username = base_username + str(random.randint(10, 99))
        cursor.execute("SELECT 1 FROM USERS WHERE username = %s", (username,))
    return username

# Ensure unique email by checking against existing emails in the database
def generate_unique_email(cursor, username):
    email = username + str(random.randint(100, 999)) + "@gmail.com"
    cursor.execute("SELECT 1 FROM USERS WHERE email = %s", (email,))
    while cursor.fetchone():  # If email exists, regenerate
        email = faker.user_name() + str(random.randint(10, 99)) + "@gmail.com"
    return email

# Function to insert data into USERS table
def insert_data():
    conn = connect_to_postgres()
    cursor = conn.cursor()

    try:
        users_data = []

        for i in range(NUM_USERS):
            # Ensure unique username and email by querying the database
            username = generate_unique_username(cursor)
            email = generate_unique_email(cursor, username)
            password = random_string(12)
            status = 'active'  # Default status
            report_count = 0  # Default report count

            users_data.append((username, password, email, status, report_count))

        # Bulk insert into USERS table and get the returned user_id
        cursor.executemany("""
            INSERT INTO USERS (username, password, email, status, report_count)
            VALUES (%s, %s, %s, %s, %s) RETURNING user_id
        """, users_data)

        # Commit and get user IDs from the returned results
        conn.commit()
        user_ids = [user_id[0] for user_id in cursor.fetchall()]

        if user_ids:
            print(f"Inserted {len(user_ids)} users.")
        else:
            print("No user IDs were returned.")
        
        # Check total users in the USERS table
        cursor.execute("SELECT COUNT(*) FROM USERS")
        count = cursor.fetchone()[0]
        print(f"Total users in the database: {count}")

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

# Main entry point
if __name__ == "__main__":
    insert_data()
