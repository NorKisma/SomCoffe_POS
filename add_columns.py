import os
from sqlalchemy import create_engine, text
from config import Config

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

try:
    with engine.connect() as con:
        con.execute(text("ALTER TABLE users ADD COLUMN evc_number VARCHAR(20)"))
        con.commit()
        print("Added evc_number")
except Exception as e:
    print(e)
    
try:
    with engine.connect() as con:
        con.execute(text("ALTER TABLE users ADD COLUMN edahab_number VARCHAR(20)"))
        con.commit()
        print("Added edahab_number")
except Exception as e:
    print(e)
