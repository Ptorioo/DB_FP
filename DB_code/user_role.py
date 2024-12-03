import psycopg2
import random
import string
from faker import Faker

# Initialize Faker
faker = Faker()

# PostgreSQL DB connection parameters
db_password = ""
DB_CONFIG = {
    'dbname': 'DB_FP',
    'user': 'postgres',
    'host': 'localhost',
    'password': db_password
}

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

# Function to insert data into USERS table
def insert_data():
    conn = connect_to_postgres()
    cursor = conn.cursor()

    try:
        # 1. Get all user_ids from USERS table
        cursor.execute("SELECT user_id FROM USERS")
        user_ids = [user_id[0] for user_id in cursor.fetchall()]

        # 2. Calculate number of admins (about 0.1% of total users)
        num_admins = max(1, int(len(user_ids) * 0.001))
        admin_ids = random.sample(user_ids, num_admins)

        roles_data = []
        
        # 3. Assign roles to users
        for user_id in user_ids:
            if user_id in admin_ids:
                # Admins get both 'Admin' and 'User' roles
                roles_data.append((user_id, 'Admin'))
                roles_data.append((user_id, 'User'))
            else:
                # Non-admins only get 'User' role
                roles_data.append((user_id, 'User'))

        # 4. Insert user roles into USER_ROLE table
        cursor.executemany("""
            INSERT INTO USER_ROLE (user_id, role)
            VALUES (%s, %s)
        """, roles_data)
        
        # Commit changes
        conn.commit()

        print(f"Successfully assigned roles to {len(roles_data)} roles.")

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

# Main entry point
if __name__ == "__main__":
    insert_data()
