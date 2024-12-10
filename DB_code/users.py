from init import *

# Number of users to generate
NUM_USERS = 120000

# Function to generate random string (for passwords)
def random_string(length):
    return ''.join(random.choices(string.ascii_letters, k=length))

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

def hash_password(password: str) -> str:
    sha1_hash = hashlib.sha1()

    sha1_hash.update(password.encode('utf-8'))
    return sha1_hash.hexdigest()[:20]


# Function to insert data into USERS table
def insert_data():
    conn = connect_to_postgres()
    cursor = conn.cursor()

    try:

        for _ in range(NUM_USERS):
            # Ensure unique username and email by querying the database
            username = generate_unique_username(cursor)
            email = generate_unique_email(cursor, username)
            password = random_string(8)
            hashed_password = hash_password(password)

            if len(username) <= 20:
                # Bulk insert into USERS table and get the returned user_id
                query = """
                    INSERT INTO USERS (username, password, email)
                    VALUES (%s, %s, %s) RETURNING user_id;
                """
                cursor.execute(query, (username, hashed_password, email))
                user_id = cursor.fetchone()[0]

                roles_query = """
                    INSERT INTO USER_ROLE (user_id, role)
                    VALUES (%s, 'User');
                """
                cursor.execute(roles_query, (user_id,))

                # Commit and get user IDs from the returned results
                conn.commit()
        
        
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
