import os
import models
import redis
import time
from fastapi import Depends, HTTPException
from auth import get_current_user

CAPACITY = 5
REFILL_RATE = 5 / 60 

REDIS_URL = os.getenv('REDIS_URL', "redis://localhost:6379/0")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def token_bucket_rate_limiter(current_user: models.User = Depends(get_current_user)):
    key = f"token_bucket:{current_user.username}"
    bucket = redis_client.hgetall(key)
    tokens = float(bucket.get("tokens", CAPACITY))
    last_refill = float(bucket.get("last_refill", time.time()))

    now = time.time()
    elapsed = now - last_refill
    new_tokens = min(CAPACITY, tokens + elapsed * REFILL_RATE)

    if new_tokens >= 1:
        new_tokens -= 1
        allowed = True
    else:
        allowed = False

    redis_client.hset(key, mapping={"tokens": new_tokens, "last_refill": now})

    if not allowed:
        raise HTTPException(status_code=429, detail="Too many requests. Please try again in a moment.")