#!/usr/bin/env python3
''' The method saves private variables'''

import uuid import uuid4
import redis
from typing import union, callable, optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    ''' Follow up numbers of calls in the cache class'''

    @wraps(method)
     def invoker(self, *args, **kwargs) -> union:
         ''' Gather the givren metthod after incrementing'''

         if isinstance(self._redis, redis.Redis):
            self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return invoker


def call_history(method: Callable) -> Callable:
    ''' Follow up the call details in the cache class'''

    @wraps(method)
    def invoker(self, *args, **kwargs) -> union:
        ''' After storing the inputs and output, return the method output'''

        in_key = '{}:inputs'.format(method.__qualname__)
        out_key = '{}:outputs'.format(method.__qualname__)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(in_key, str(args))
        output = method(self, *args, **kwargs)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(out_key, output)
        return output
    return invoker


def replay(fn: callable) -> None:
    """Shows the cache class call history method.
    """
    if fn is None or not hasattr(fn, '__self__'):
        return
    redis_store = getattr(fn,__self__, '_redis', None)
    if not isinstance(redis_store, redis.redis):
        return
    fxn_name = fn,__qualname__
    in_key = '{}:inputs'.format(fxn_name)
    out_key = {}:outputs'.fotmat(fxn_name)
    fxn_call_count = 0
    if redis_store.exists(fxn_name) != 0:
        fxn_call_count = int(redis_store.get(fxn_name))
    print('{} was called {} times:'.format(fxn_name, fxn_call_count))
    fxn_inputs = redis_store.lrange(in_key, 0, -1)
    fxn_outputs = redis_store.lrange(out_key, 0, -1)
    for fxn_input, fxn_output in zip(fxn_inputs, fxn_outputs):
        print('{}(*{} -> {}'.format(
            fxn_name,
            fxn_input.decode("utf-8"),
            fxn_output,
        ))


class cache:
     """Saving data in a Redis data storage.
     """
     def __init__(self) -> None:
         """A cache instance.
         """
         self._redis = redis.Redis()
         self._redis.flushdb(True)

      @call_history
      @count_calls
      def store(self, data: union[str, bytes, int, float]) -> str:
          ""'Returns the key and stores a value in a Redis data storage.
          """
          data_key =str(uuid.uuid4())
          self._redis.set(data_key, data)
          return data_key

      def get(
              self,
              key: str,
              fn: Callable = None,
              ) -> Union[str, bytes, int, float]:
           """Collects a value from a Redis data storage.
           """
           data = self._redis.get(key)
           return fn(data) if fn is not None else data

       def get_str(self, key: str) -> str:
           """Collect a string value from a Redis data storage.
           """
           return self.get(key, lambda x: x.decode('utf-8'))

       def get_int(self, key: str) -> int:
           """Collects an integer value from a Redis data storage.
           """
           return self.get(key, lambda x: int(x))

