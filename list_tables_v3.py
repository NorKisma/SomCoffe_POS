import sqlite3
db_path = r'c:\Users\hp\OneDrive\Desktop\SomCoffe_POS\somcoffe.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
for t in cursor.fetchall():
    print(t[0])
conn.close()
