import numpy as np
from pathlib import Path
from typing import Callable

def path_default(default: str|Path, base_dir=None) -> Callable:
    '''
    Preprocess the first argument of a function to be a Path object if it is a string; also set a default value for the argument.
    Note however the first argument must not be passed in as a keyword argument.
    '''
    if not base_dir:
        base_dir = Path.cwd()
    def decorator(fn):
        def inner(*args, some_path=None, **kwargs):
            if args and some_path is None:
                some_path = args[0]
                args = args[1:]
            if some_path is None:
                some_path = default
            if isinstance(some_path, str):
                some_path = base_dir / some_path
            return fn(some_path, *args, **kwargs)

        return inner

    return decorator


def evenly_get(arr, n):
    '''
    Get n elements from arr as evenly as possible.
    Return both the elements and their indices.
    '''
    idx = np.round(np.linspace(0, len(arr) - 1, n)).astype(int)
    return np.asarray(arr)[idx], idx
