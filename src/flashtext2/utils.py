from __future__ import annotations

__all__ = [
    'yield_nested_dict_items',
    'convert_trie_to_dict',
]

from typing import Iterator, Any


def yield_nested_dict_items(dct: dict) -> Iterator[tuple[str, Any]]:
    """
    A generator that yields the keys and values from nested dictionaries

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


def convert_trie_to_dict(
        dct: dict[str, dict | str],
        s: str = '',
        mapping: dict | None = None
) -> dict[str, str]:
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

# TODO: replace all `__keyword__` with `True`
