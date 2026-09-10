import os
import mysql.connector
from mysql.connector import Error

# Helper to load .env manually in case python-dotenv is not installed
def load_env_manually(filepath=".env"):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    # Strip quotes if present
                    value = value.strip('"\'')
                    os.environ[key.strip()] = value

def test_connection():
    # Load environment variables
    load_env_manually()

    # Get connection details from environment variables
    db_host = os.environ.get("DB_HOST")
    db_user = os.environ.get("DB_USER")
    db_password = os.environ.get("DB_PASSWORD")
    db_port = os.environ.get("DB_PORT", "3306")
    
    print(f"Attempting to connect to MySQL on {db_host}:{db_port} as user '{db_user}'...")

    try:
        # Establish the connection
        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            port=int(db_port),
            use_pure=True
        )

        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"Successfully connected to MySQL Server version {db_info}")
            
            # Fetch some basic info to prove it works
            cursor = connection.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            print(f"You're connected to database: {record[0]}")
            
            # Close cursor and connection
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")
            
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")

if __name__ == "__main__":
    test_connection()
