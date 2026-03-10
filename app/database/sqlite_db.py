# SQLite specific engine configuration
# Used when DB_MODE=offline
import os

def get_sqlite_uri(base_dir):
    return 'sqlite:///' + os.path.join(base_dir, 'somcoffe.db')
