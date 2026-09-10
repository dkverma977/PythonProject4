import mysql.connector
import sys

try:
    print("Attempting to connect...")
    conn = mysql.connector.connect(host='10.1.40.11', port=3306, user='dev_user1', password='sagar@1729',
    connection_timeout=10,
    use_pure=True)
    print("Connection successful", conn)
except Exception as e:
    print("Connection failed:", type(e), e)
    sys.exit(1)
