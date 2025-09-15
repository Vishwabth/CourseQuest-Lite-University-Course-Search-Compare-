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
    """Delete all cache keys with the given prefix (Redis + fallback)."""
    pattern = f"{prefix}*"
    cleared = 0

    # Redis
    if redis_client:
        try:
            for key in redis_client.scan_iter(pattern):
                redis_client.delete(key)
                cleared += 1
            logging.info(f"[Cache] Cleared {cleared} Redis keys for prefix '{prefix}'")
        except Exception as e:
            logging.warning(f"Redis error on clear_cache_prefix: {e}")

    # Fallback (in-memory)
    to_delete = [k for k in cache_store.keys() if k.startswith(prefix)]
    for k in to_delete:
        del cache_store[k]
        cleared += 1

    logging.info(f"[Cache] Cleared {cleared} total keys (Redis + memory) for prefix '{prefix}'")
