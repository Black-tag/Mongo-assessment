import redis.asyncio as aioredis
from fastapi import Depends
import json


_client = None


def init_redis():
    global _client

    _client = aioredis.Redis(
        host="localhost",
        port=6379,
        username="blacktag",
        password="161718",
        decode_responses=True,
    )
    return _client


async def get_client():
    if _client is None:
        raise RuntimeError("Redis not initialised")
    else:
        return _client


async def get_cache(key):
    client = await get_client()

    result = await client.get(key)

    if result is None:
        return None
    return json.loads(result)


async def set_cache(key, value, ttl=300):
    client = await get_client()

    result = await client.setex(key, ttl, json.dumps(value, default=str))

    if not result:
        return "cache set failed"
    return "cache set succesfully"
