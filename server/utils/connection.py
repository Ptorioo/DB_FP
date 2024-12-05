import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = "DB_FP"
DB_USER = "postgres"
DB_HOST = "localhost"
DB_PASSWORD = os.getenv("PASSWORD")
DB_PORT = os.getenv("PORT")

def db_connect():
    try:
        global db
        db = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )

        global cur
        cur = db.cursor()

        return db
    
    except Exception as err:
        print("Internal Error: ", err)
        raise err