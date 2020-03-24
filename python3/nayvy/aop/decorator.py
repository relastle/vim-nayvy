import time
from typing import Any
from functools import wraps


def measure_time(f: Any) -> Any:
    @wraps(f)
    def timed(*args: Any, **kw: Any) -> Any:
        start = time.time()
        result = f(*args, **kw)
        print(f'[Nayvy: {f.__name__}] Elapsed time = {time.time() - start:5.3f}s')
        return result
    return timed
