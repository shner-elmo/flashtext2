from __future__ import annotations

from typing import Generator, Any, TypeVar


__all__ = [
    'yield_nested_dict_items',
    'convert_trie_to_dict',
]

T = TypeVar('T')


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
