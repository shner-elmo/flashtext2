from __future__ import annotations

import itertools
from collections import deque
from typing import Generator, Any


class TrieDictException(Exception):
    """
    Base TrieDict Exception
    """
    pass


class WordNotFoundError(TrieDictException):
    """
    Raised when given word isn't present in the tree data structure
    """
    pass


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
    __slots__ = ('trie_dict', '_words_count')
    keyword = '__keyword__'

    def __init__(self) -> None:
        self._words_count = 0
        self.trie_dict = {}

    def add_word(self, word: str) -> None:
        node = self.trie_dict
        for char in word:
            node = node.setdefault(char, {})

        node[TrieDict.keyword] = word
        self._words_count += 1

    def remove_word(self, word: str) -> None:
        last_bi_node_idx = None  # index of the character that its node contains multiple children
        for idx, node in enumerate(self.node_iterator(word)):
            if len(node) > 1:
                last_bi_node_idx = idx

        node.pop(TrieDict.keyword)  # noqa # Local variable 'node' might be referenced before assignment

        if len(self.get_children(node)) == 0:  # last node has no children, so we can safely delete prior nodes
            if last_bi_node_idx is None:
                self.trie_dict.pop(word[0])  # remove the beginning of the tree
            else:
                # remove all the nodes between the last node that had multiple children and the last letter of our word
                chars_seq = word[:last_bi_node_idx + 1]
                first_char_to_remove = word.removeprefix(chars_seq)[0]
                self.get_node(word=chars_seq).pop(first_char_to_remove)
        self._words_count -= 1

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
                    f'Not able to locate {word} in the Trie Dict. (failed at character "{word[idx]}")')
            yield node

    def get_node(self, word: str) -> dict:
        """
        Get the node containing the last character of the word (works for substrings of any word)
        """
        return deque(self.node_iterator(word), 1)[0]

    @staticmethod
    def get_children(node: dict) -> list[str]:
        """
        Get all the children from a given node (characters)
        """
        return [k for k in node if k != TrieDict.keyword]

    def has_word(self, word: str) -> bool:
        return word in self

    def get_words(self, n: int | None = None) -> list[str]:
        """
        Get n amount of words from the  Trie Dict
        """
        return list(itertools.islice(self, n))

    def reset_dict(self) -> None:
        self.__init__()

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
        return repr(self.get_words(30))

    def __repr__(self) -> str:
        """
        Get the Trie Dictionary
        """
        return repr(self.trie_dict)


def main():
    import random

    pairs = [
        ({}, []),
        ({'a': {}}, [('a', None)]),
        ({'a': {}, 'b': {}, 'c': 3, 'd': None, 'e': []},
         [('a', None), ('b', None), ('c', 3), ('d', None), ('e', [])]),
        ({'a': {'b': {}, 'key': True}}, [('a', None), ('b', None), ('key', True)]),
    ]
    for input_, output in pairs:
        assert list(recursive_get_dict_items(input_)) == output

    similar_words = [
        'macaco',
        'macaroni',
        'macaroon',
        'machinable',
        'machine',
        'macromolecular',
        'macro',
        'macroscopic',
        'macronuclear'
    ]
    td = TrieDict()
    for word in similar_words:
        td.add_word(word)
    assert len(td) == len(similar_words)
    assert sorted(td.get_words()) == sorted(similar_words)

    for word in similar_words:
        assert td.has_word(word)

    random.shuffle(similar_words)
    non_removed_words = similar_words
    for word in similar_words:
        print(td)
        print(repr(td))
        print('-' * 100)

        assert td.has_word(word)

        td.remove_word(word)
        non_removed_words.remove(word)

        assert not td.has_word(word)

        rand_words = random.choices(non_removed_words, k=min(3, len(non_removed_words)))
        for w in rand_words:
            assert w in td


if __name__ == '__main__':
    main()

# notes:
# TODO try removing the try/except block and see how the performance differs
