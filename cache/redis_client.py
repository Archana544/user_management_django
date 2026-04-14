# cache/redis_client.py
import redis.asyncio as redis
import json
from typing import Any, Optional
from datetime import timedelta

class RedisCache:
    def __init__(self, url: str = "redis://localhost:6379"):
        self.client = redis.from_url(
            url,
            decode_responses=True,  
            max_connections=10
        )

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = await self.client.get(key)
            if value is None:
                return None
            return json.loads(value)
        except Exception as e:
            logger.error("redis_get_error", key=key, error=str(e))
            return None  # fail silently — don't crash app

    async def set(
        self,
        key:   str,
        value: Any,
        ttl:   int = 300  # seconds
    ) -> bool:
        """Set value in cache with TTL"""
        try:
            serialized = json.dumps(value)
            await self.client.setex(
                key,
                timedelta(seconds=ttl),
                serialized
            )
            return True
        except Exception as e:
            logger.error("redis_set_error", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """Delete from cache"""
        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            logger.error("redis_delete_error", error=str(e))
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            keys = await self.client.keys(pattern)
            if keys:
                await self.client.delete(*keys)
            return len(keys)
        except Exception as e:
            logger.error("redis_delete_pattern_error", error=str(e))
            return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        return bool(await self.client.exists(key))

    async def increment(
        self, key: str, ttl: int = 60
    ) -> int:
        """Atomic increment — used for rate limiting"""
        pipe = self.client.pipeline()
        await pipe.incr(key)
        await pipe.expire(key, ttl)
        results = await pipe.execute()
        return results[0]

cache = RedisCache()