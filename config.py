import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'somcoffe-pos-secret-key-2026'
    
    # --- Database Configuration ---
    # To use MySQL: Set DB_MODE=online in .env and provide ONLINE_DATABASE_URL
    # To use SQLite: Set DB_MODE=offline in .env
    
    DB_MODE = os.environ.get('DB_MODE', 'online').lower()
    
    # 1. Base SQLite path (Guaranteed Fallback)
    sqlite_uri = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'somcoffe.db')
    
    # 2. MySQL / Remote database URL (from .env)
    # Default format: mysql+pymysql://username:password@localhost/db_name
    online_uri = os.environ.get('ONLINE_DATABASE_URL')
    
    if DB_MODE == 'online' and online_uri:
        SQLALCHEMY_DATABASE_URI = online_uri
    elif DB_MODE == 'online' and not online_uri:
        # If online mode but no URL, you can provide a local MySQL default here
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root@localhost/somcoffe_pos'
    else:
        # Fallback to Local Offline SQLite
        SQLALCHEMY_DATABASE_URI = sqlite_uri

    # Performance & Stability for MySQL (Pool handling)
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20
    }

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
