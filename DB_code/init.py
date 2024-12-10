import psycopg2
import random
import string
import hashlib
from faker import Faker

# Initialize Faker
faker = Faker()

# PostgreSQL DB connection parameters
db_password = "" # fill in your password
DB_CONFIG = {
    'dbname': 'DB_FP_new',
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
