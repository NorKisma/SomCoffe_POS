import sqlite3
db_path = r'c:\Users\hp\OneDrive\Desktop\SomCoffe_POS\somcoffe.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(orders);")
columns = [row[1] for row in cursor.fetchall()]
print(f"Orders columns: {', '.join(columns)}")
conn.close()
