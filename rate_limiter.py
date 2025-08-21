import redis
import logging

class RateLimiter:
    """
    Redis-backed rate limiter per client (IP)
    """
    def __init__(self, redis_client, limit=5, window=60):
        self.r = redis_client
        self.limit = limit
        self.window = window

    def allow_request(self, client_id):
        key = f"rate:{client_id}"
        try:
            count = self.r.incr(key)
            if count == 1:
                self.r.expire(key, self.window)
            return count <= self.limit
        except Exception as e:
            logging.warning(f"RateLimiter error: {e}")
            return True