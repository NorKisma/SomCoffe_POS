from flask_caching import Cache

# Simple in-memory cache (no Redis needed in development).
# To use Redis in production, set CACHE_TYPE=RedisCache in config.
cache = Cache()
