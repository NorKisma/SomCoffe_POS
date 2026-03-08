import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'somcoffe-pos-secret-key-2026'
    
    # --- Hybrid Database Logic (Dual-Mode) ---
    # ONLINE: MySQL (Remote Host)
    # OFFLINE: SQLite (Local File)
    
    DB_MODE = os.environ.get('DB_MODE', 'offline').lower()
    
    # 1. Base SQLite path (Always available)
    sqlite_uri = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'somcoffe.db')
    
    # 2. Get Remote / Online DB URL 
    online_uri = os.environ.get('ONLINE_DATABASE_URL')
    
    if DB_MODE == 'online' and online_uri:
        SQLALCHEMY_DATABASE_URI = online_uri
    else:
        # Default to Offline (SQLite)
        SQLALCHEMY_DATABASE_URI = sqlite_uri

    # File Uploads
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 16 MB

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Mail Settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')
    
    DEBUG = True
