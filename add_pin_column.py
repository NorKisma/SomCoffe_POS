import sqlite3
import os
from sqlalchemy import create_engine, text

# Get DB URI from .env or config
# For simplicity, let's assume it's SQLite as it's the most common local setup
db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'somcoffe.db')

if os.path.exists(db_path):
    print(f"Adding columns to SQLite at {db_path}...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute("ALTER TABLE users ADD COLUMN pin VARCHAR(10)")
        print("Column 'pin' added to users table.")
    except Exception as e:
        print(f"Error adding 'pin': {e}")
    conn.commit()
    conn.close()

# If using MySQL (from .env)
from dotenv import load_dotenv
load_dotenv()
online_uri = os.environ.get('ONLINE_DATABASE_URL')
if online_uri:
    print("Adding columns to Remote DB...")
    engine = create_engine(online_uri)
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN pin VARCHAR(10)"))
            conn.commit()
            print("Column 'pin' added to users table (Remote).")
        except Exception as e:
            print(f"Error adding 'pin' (Remote): {e}")

# Also add columns to settings if needed? No, Setting table structure is fine.
# But we should ensure default values are there.
