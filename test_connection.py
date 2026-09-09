import mysql.connector
from mysql.connector import Error

print("Script started...")

def test_connection():
    try:
        print("Attempting to connect...")
        # NOTE: Please update these placeholders with your actual IP and credentials again
        connection = mysql.connector.connect(
            host='10.1.40.11',
            database='master_data',
            user='dev_user1',
            password='sagar@1729'
        )
        print("Connect call finished.")
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"Successfully connected to MySQL Server version {db_info}")
            cursor = connection.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            print(f"You're connected to database: {record[0]}")
        else:
            print("Connect succeeded, but connection.is_connected() returned False.")

    except Error as e:
        print(f"MySQL Error: {e}")
    except Exception as e:
        print(f"Other Error: {e}")
    finally:
        print("Entering finally block...")
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

if __name__ == '__main__':
    test_connection()
    print("Script finished.")
