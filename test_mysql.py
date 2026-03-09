import os
from dotenv import load_dotenv
import pymysql
import sys

load_dotenv()

conn_url = os.environ.get('ONLINE_DATABASE_URL')
print(f"Testing connection to: {conn_url}")

# Extract parts manually to test
# mysql+pymysql://root:@localhost/somcoffe?charset=utf8mb4
try:
    if not conn_url:
        print("ONLINE_DATABASE_URL not set in .env")
        sys.exit(1)
        
    # Basic parse
    part1 = conn_url.split('://')[1]
    part2 = part1.split('@')
    user_pass = part2[0].split(':')
    user = user_pass[0]
    password = user_pass[1] if len(user_pass) > 1 else ''
    
    rest = part2[1].split('/')
    host_port = rest[0].split(':')
    host = host_port[0]
    port = int(host_port[1]) if len(host_port) > 1 else 3306
    
    db_query = rest[1].split('?')
    db = db_query[0]
    
    print(f"User: {user}, Host: {host}, Port: {port}, DB: {db}")
    
    conn = pymysql.connect(
        host=host,
        user=user,
        password=password,
        port=port,
        database=db
    )
    print("Successfully connected to MySQL!")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
