from __future__ import annotations

import functools
import inspect

from typing import TYPE_CHECKING, Callable, Generator, Any, Sequence, Iterator, TypeVar

if TYPE_CHECKING:
    from .keyword_processor import TrieDict

__all__ = [
    'normalize_parameter',
    'yield_nested_dict_items',
    'convert_trie_to_dict',
    'enumerate_shifted',
]

T = TypeVar('T')


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


def yield_nested_dict_items(dct: dict) -> Generator[tuple[str, Any], None, None]:
    """
    A generator that gets the keys and values from nested dictionaries

    :return: Generator
    :yields: (key, None) if value is dict else (key, val)
    """
    for k, v in dct.items():
        if isinstance(v, dict):
            yield k, None
            for tup in yield_nested_dict_items(v):
                yield tup
        else:
            yield k, v


def convert_trie_to_dict(dct: dict[str, dict | str], s: str = '', mapping: dict | None = None) -> dict[str, str]:
    """
    Convert a Trie Dict to a flat dictionary (recursively)

    :param dct: dictionary to flatten
    :param s: string (this should be left empty as the function will fill this recursively)
    :param mapping: dictionary mapping (constructed by the function)
    :return: a flat dictionary: `{word1: clean_word1, word2: clean_word2, ...}`
    """
    if mapping is None:
        mapping = {}

    for key, val in dct.items():
        if key == '__keyword__':  # key == TrieDict.keyword
            mapping[s] = val
        elif isinstance(val, dict):
            convert_trie_to_dict(val, s=s + key, mapping=mapping)
    return mapping


# list(enumerate_shifted('abcdef', start=3)) == ['d', 'e', 'f']
def enumerate_shifted(seq: Sequence[T], start: int) -> Iterator[tuple[int, T]]:
    for i in range(start, len(seq)):
        yield i, seq[i]
