# MySQL specific engine configuration
# Used when DB_MODE=online
def get_mysql_options():
    return {
        "pool_recycle": 280,
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20
    }
