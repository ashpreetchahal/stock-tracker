import redis
import logging

class RedisCache:
    """Simple Redis wrapper"""
    def __init__(self, host='localhost', port=6379, db=0):
        self.r = redis.Redis(host=host, port=port, db=db)

    def get(self, key):
        try:
            value = self.r.get(key)
            return value.decode() if value else None
        except Exception as e:
            logging.warning(f"Redis GET error: {e}")
            return None

    def set_with_expiry(self, key, value, seconds):
        try:
            self.r.setex(key, seconds, value)
        except Exception as e:
            logging.warning(f"Redis SET error: {e}")