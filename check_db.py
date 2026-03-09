import sqlite3
import os

db_path = r'c:\Users\hp\OneDrive\Desktop\SomCoffe_POS\somcoffe.db'
if not os.path.exists(db_path):
    print(f"Database file {db_path} not found.")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    print(f"Tables: {', '.join(tables)}")
    
    if 'alembic_version' in tables:
        cursor.execute("SELECT version_num FROM alembic_version")
        version = cursor.fetchone()
        print(f"Alembic Version: {version[0] if version else 'Empty'}")
        
    if 'customers' in tables:
        cursor.execute("SELECT count(*) FROM customers")
        count = cursor.fetchone()[0]
        print(f"Customers count: {count}")
    conn.close()
