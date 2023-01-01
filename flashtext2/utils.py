from __future__ import annotations

import functools
import inspect

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from .keyword_processor import TrieDict

__all__ = ['normalize_parameter']


def normalize_parameter(*params: str) -> Callable:
    """
    Instead of doing this at the beginning of each function:
    if not self.case_sensitive:
        word = word.lower()

    We can just decorate the function with: `@normalize_parameter('parameter_name')`

    :param params: parameter names
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            kwargs = inspect.getcallargs(func, *args, **kwargs)  # convert all args and def parameters to dict/kwargs
            self: TrieDict = kwargs['self']

            if not self._case_sensitive:
                for p in params:
                    value = kwargs.get(p)
                    if value:
                        kwargs[p] = value.lower()

            return func(**kwargs)
        return wrapper
    return decorator
