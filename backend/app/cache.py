import os
import redis
import logging

# Global Redis client
redis_client = None
cache_store = {}  # fallback in-memory cache

def init_cache():
    """Initialize Redis client if available."""
    global redis_client
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        try:
            redis_client = redis.Redis.from_url(redis_url, decode_responses=False)
            redis_client.ping()
            logging.info("✅ Connected to Redis")
        except Exception as e:
            redis_client = None
            logging.warning(f"⚠️ Could not connect to Redis, using in-memory cache. Error: {e}")

def get_cache(key: str):
    if redis_client:
        try:
            val = redis_client.get(key)
            if val:
                return val.decode("utf-8")
        except Exception as e:
            logging.warning(f"Redis error: {e}")
    return cache_store.get(key)

def set_cache(key: str, value: str, ttl: int = 60):
    if redis_client:
        try:
            redis_client.setex(key, ttl, value)
            return
        except Exception as e:
            logging.warning(f"Redis error: {e}")
    cache_store[key] = value

def clear_cache_prefix(prefix: str):
    """Delete all cache keys with the given prefix and log it."""
    if redis_client:
        try:
            pattern = f"{prefix}*"
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
                print(f"[Cache] Cleared {len(keys)} keys for prefix '{prefix}'")
            else:
                print(f"[Cache] No keys found for prefix '{prefix}'")
        except Exception as e:
            logging.warning(f"Redis error on clear_cache_prefix: {e}")
