"""
Redis cache service for performance optimization
"""

import asyncio
import json
import logging
from typing import Any, Optional, Dict, List
from datetime import timedelta

import redis.asyncio as redis

from app.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Redis-based cache service"""
    
    def __init__(self):
        self.redis_client = None
        self._lock = asyncio.Lock()
        
    async def connect(self):
        """Connect to Redis"""
        async with self._lock:
            if self.redis_client is None:
                try:
                    self.redis_client = redis.from_url(
                        settings.REDIS_URL,
                        decode_responses=True,
                        max_connections=settings.REDIS_POOL_SIZE
                    )
                    # Test connection
                    await self.redis_client.ping()
                    logger.info("Connected to Redis")
                except Exception as e:
                    logger.error(f"Failed to connect to Redis: {e}")
                    self.redis_client = None
                    raise
                    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
            logger.info("Disconnected from Redis")
            
    async def ping(self) -> bool:
        """Check Redis connectivity"""
        try:
            if self.redis_client:
                return await self.redis_client.ping()
            return False
        except Exception:
            return False
            
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        try:
            if self.redis_client:
                return await self.redis_client.get(key)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
            
    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> bool:
        """Set value in cache"""
        try:
            if self.redis_client:
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                return await self.redis_client.set(key, value, ex=expire)
            return False
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
            
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            if self.redis_client:
                return await self.redis_client.delete(key) > 0
            return False
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
            
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            if self.redis_client:
                return await self.redis_client.exists(key) > 0
            return False
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False
            
    async def incr(self, key: str) -> Optional[int]:
        """Increment counter in cache"""
        try:
            if self.redis_client:
                return await self.redis_client.incr(key)
            return None
        except Exception as e:
            logger.error(f"Cache incr error: {e}")
            return None
            
    async def decr(self, key: str) -> Optional[int]:
        """Decrement counter in cache"""
        try:
            if self.redis_client:
                return await self.redis_client.decr(key)
            return None
        except Exception as e:
            logger.error(f"Cache decr error: {e}")
            return None
            
    async def ttl(self, key: str) -> Optional[int]:
        """Get time to live for key"""
        try:
            if self.redis_client:
                ttl = await self.redis_client.ttl(key)
                return ttl if ttl >= 0 else None
            return None
        except Exception as e:
            logger.error(f"Cache ttl error: {e}")
            return None
            
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for key"""
        try:
            if self.redis_client:
                return await self.redis_client.expire(key, seconds)
            return False
        except Exception as e:
            logger.error(f"Cache expire error: {e}")
            return False
            
    async def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern"""
        try:
            if self.redis_client:
                return await self.redis_client.keys(pattern)
            return []
        except Exception as e:
            logger.error(f"Cache keys error: {e}")
            return []
            
    async def flushdb(self) -> bool:
        """Flush current database"""
        try:
            if self.redis_client:
                return await self.redis_client.flushdb()
            return False
        except Exception as e:
            logger.error(f"Cache flushdb error: {e}")
            return False
            
    # Cache-specific methods
    
    async def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        """Get JSON value from cache"""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None
        
    async def set_json(
        self,
        key: str,
        value: Dict[str, Any],
        expire: Optional[int] = None
    ) -> bool:
        """Set JSON value in cache"""
        return await self.set(key, json.dumps(value), expire)
        
    # Rate limiting methods
    
    async def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> tuple[bool, int]:
        """
        Check if request is within rate limit
        
        Args:
            key: Rate limit key (e.g., user_id + endpoint)
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        try:
            if not self.redis_client:
                return True, max_requests  # Allow if Redis is down
                
            # Use sliding window algorithm
            current_time = asyncio.get_event_loop().time()
            window_key = f"rate_limit:{key}:{int(current_time // window_seconds)}"
            
            # Increment counter
            count = await self.incr(window_key)
            
            # Set expiration if this is the first request in window
            if count == 1:
                await self.expire(window_key, window_seconds)
                
            is_allowed = count <= max_requests
            remaining = max(0, max_requests - count)
            
            return is_allowed, remaining
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True, max_requests  # Allow if Redis is down
            
    # Cache warming and invalidation
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern"""
        try:
            if not self.redis_client:
                return 0
                
            keys = await self.keys(pattern)
            if keys:
                return await self.redis_client.delete(*keys)
            return 0
            
        except Exception as e:
            logger.error(f"Pattern invalidation failed: {e}")
            return 0
            
    async def warm_cache(self, key: str, data_func, expire: int = 3600):
        """
        Warm cache with data if not already cached
        
        Args:
            key: Cache key
            data_func: Async function to generate data if not in cache
            expire: Cache expiration time
        """
        try:
            # Check if data is already cached
            cached_data = await self.get_json(key)
            if cached_data:
                return cached_data
                
            # Generate data and cache it
            data = await data_func()
            await self.set_json(key, data, expire)
            
            return data
            
        except Exception as e:
            logger.error(f"Cache warming failed: {e}")
            # Return data without caching
            return await data_func()
            
    # Cache statistics
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            if not self.redis_client:
                return {"status": "disconnected"}
                
            info = await self.redis_client.info()
            return {
                "status": "connected",
                "version": info.get("redis_version"),
                "connected_clients": info.get("connected_clients"),
                "used_memory": info.get("used_memory_human"),
                "total_commands_processed": info.get("total_commands_processed"),
                "keyspace_hits": info.get("keyspace_hits"),
                "keyspace_misses": info.get("keyspace_misses")
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"status": "error", "error": str(e)}


# Global cache service instance
cache_service = CacheService()


async def get_cache_service() -> CacheService:
    """Get cache service (dependency)"""
    await cache_service.connect()
    return cache_service