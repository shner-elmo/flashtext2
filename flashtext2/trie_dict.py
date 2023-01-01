from __future__ import annotations

import itertools
from collections import deque
from typing import Union, Generator, Any

from .utils import normalize_parameter
from .exceptions import WordNotFoundError


def recursive_get_dict_items(dct: dict) -> Generator[tuple[str, Any], None, None]:
    """
    A generator that gets the keys and values from nested dictionaries

    :return: A Generator that yields a tuple with the key and value
    """
    for k, v in dct.items():
        if isinstance(v, dict):
            yield k, None
            for tup in recursive_get_dict_items(v):
                yield tup
        else:
            yield k, v


class TrieDict:
    __slots__ = ('_case_sensitive', 'trie_dict', '_words_count')
    keyword = '__keyword__'

    def __init__(self, case_sensitive: bool = False) -> None:
        self._case_sensitive = case_sensitive  # shouldn't be changed after __init__()
        self._words_count = 0
        self.trie_dict = {}

    @normalize_parameter('word', 'clean_word')
    def add_keyword(self, word: str, clean_word: Union[str, None] = None) -> None:
        if word in self:
            return  # to avoid increasing the counter
        node = self.trie_dict
        for char in word:
            node = node.setdefault(char, {})

        node[TrieDict.keyword] = clean_word or word
        self._words_count += 1

    @normalize_parameter('word')
    def remove_keyword(self, word: str) -> None:
        if word not in self:
            raise WordNotFoundError(f"No such word: '{word}'")

        last_multi_node_idx = None  # index of the character that its node contains multiple children
        for idx, node in enumerate(self.node_iterator(word)):
            if len(node) > 1:  # node either has children or is a keyword
                last_multi_node_idx = idx

        del node[TrieDict.keyword]  # noqa # Local variable 'node' might be referenced before assignment

        if len(node) == 0:  # if last node has no children we can safely delete prior nodes
            if last_multi_node_idx is None:
                self.trie_dict.pop(word[0])  # remove the beginning of the tree
            else:
                # remove all the nodes between the last node that had multiple children and the last letter of our word
                chars_seq = word[:last_multi_node_idx + 1]  # node characters that we need to keep
                first_char_to_remove = word.removeprefix(chars_seq)[0]
                last_node = deque(self.node_iterator(word=chars_seq), maxlen=1)[0]  # iterate in C and keep last item
                del last_node[first_char_to_remove]
        self._words_count -= 1

    @normalize_parameter('word')
    def node_iterator(self, word: str) -> Generator[dict, None, None]:
        """
        Yield each node (dictionary) for each character in the word
        """
        node = self.trie_dict
        for idx, char in enumerate(word):
            try:
                node = node[char]
            except KeyError:
                raise WordNotFoundError(
                    f'Not able to locate "{word}" in the Trie Dict. (failed at character "{word[idx]}")')
            yield node

    @normalize_parameter('word')
    def has_word(self, word: str) -> bool:
        return word in self

    def get_keywords(self, n: Union[int, None] = None) -> list[str]:
        """
        Get n amount of words from the Trie Dict
        """
        return list(itertools.islice(self, n))

    def reset_dict(self) -> None:
        self.__init__()

    @normalize_parameter('word')
    def __contains__(self, word: str) -> bool:
        """
        Check if each character from the given word is present in the Trie Dict,
        and that the last node is marked as a keyword.
        (so 'mac' wouldn't be present if 'machine' is the only word in the Trie Dict)
        """
        node = self.trie_dict
        for char in word:
            node = node.get(char)
            if node is None:
                return False
        return node.get(TrieDict.keyword) == word

    def __iter__(self) -> Generator[str, None, None]:
        """
        Get all words in the Trie Dict
        """
        for k, v in recursive_get_dict_items(self.trie_dict):
            if k == TrieDict.keyword:
                yield v

    def __len__(self) -> int:
        return self._words_count

    def __eq__(self, other) -> bool:
        if not isinstance(other, TrieDict) or len(self) != len(other):
            return False
        return self.trie_dict == other.trie_dict

    def __str__(self) -> str:
        """
        Get first 30 words
        """
        return str(self.get_keywords(30))

    def __repr__(self) -> str:
        """
        Get the Trie Dictionary
        """
        return repr(self.trie_dict)
