import logging
from functools import wraps
import time
from typing import Callable, Any

def async_timed(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        logging.info(f"任务 {func.__name__} 开始执行")
        start = time.perf_counter()
        try:
            return await func(*args, **kwargs)
        finally:
            end = time.perf_counter()
            total = end - start
            logging.info(f"任务 {func.__name__} 用 {total} 秒执行完毕")
    return wrapper
