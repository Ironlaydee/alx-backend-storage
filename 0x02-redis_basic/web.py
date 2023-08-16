
#!/usr/bin/env python3
''' Tools for request caching and tracking'''

import redis
import requests
from typing import callable
from functools import wraps


redis_store = redis.Redis()
''' Simulate a slow response and test your caching'''



def data_cacher(method: Callable) -> Callable:
    ''' Output of data fetched'''

    @wraps(method)
    def invoker(url) -> str:
        ''' The core function is very simple'''

        redis_store.incr(f'count:{url}')
        result = redis_store.get(f'result:{url}')
        if result:
            return result.decode('utf-8')
        result = method(url)
        redis_store.set(f'count:{url}', 0)
        redis_store.setex(f'result:{url}', 10, result)
        return result
    return invoker


@data_cacher
def get_page(url: str) -> str:
    ''' track how many times a particular URL was accessed in the key
    and cache the result with an expiration time of 10 seconds'''

    return requests.get(url).text
