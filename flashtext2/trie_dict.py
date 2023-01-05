from __future__ import annotations

from collections import deque
from typing import Iterable, Iterator

from .exceptions import WordNotFoundError


class TrieDict:
    __slots__ = ('_case_sensitive', '_trie_dict', '_keywords_dict')
    keyword = '__keyword__'

    def __init__(self, case_sensitive: bool = False) -> None:
        self._case_sensitive = case_sensitive  # shouldn't be changed after __init__()
        self._trie_dict = {}
        self._keywords_dict: dict[str, str] = {}  # dict[word, clean_word]

    @property
    def trie_dict(self) -> dict:
        """
        Get the dictionary containing the trie tree
        """
        return self._trie_dict

    @property
    def get_keywords(self) -> dict[str, str]:
        """
        Get the dictionary containing all the words and their corresponding clean words
        """
        return self._keywords_dict

    def add_keyword(self, word: str, clean_word: str | tuple | None = None) -> None:
        """
        Add a given keyword to the trie dict

        :param word: str
        :param clean_word: str, optional
        :return: None
        """
        if not clean_word:
            clean_word = word
        if not self._case_sensitive:
            word = word.lower()

        node = self._trie_dict
        for char in word:
            node = node.setdefault(char, {})

        node[TrieDict.keyword] = clean_word
        self._keywords_dict[word] = clean_word

    def remove_keyword(self, word: str) -> None:
        """
        Remove a keyword from the trie dict

        :param word: str
        :return: None
        :raises WordNotFoundError: if the word is not present in the trie dict
        """
        if not self._case_sensitive:
            word = word.lower()
        if word not in self:
            raise WordNotFoundError(f"No such word: '{word}'")

        last_multi_node_idx = None  # index of the character that its node contains multiple children
        for idx, node in enumerate(self._node_iterator(word)):
            if len(node) > 1:  # node either has children or is a keyword
                last_multi_node_idx = idx
        # noinspection PyUnboundLocalVariable
        del node[TrieDict.keyword]

        if len(node) == 0:  # if last node has no children we can safely delete prior nodes
            if last_multi_node_idx is None:
                self._trie_dict.pop(word[0])  # remove the beginning of the tree
            else:
                # remove all the nodes between the last node that had multiple children and the last letter of our word
                chars_seq = word[:last_multi_node_idx + 1]  # node characters that we need to keep
                first_char_to_remove = word.removeprefix(chars_seq)[0]
                last_node = deque(self._node_iterator(word=chars_seq), maxlen=1)[0]  # iterate in C and keep last item
                del last_node[first_char_to_remove]

        del self._keywords_dict[word]

    def _node_iterator(self, word: str) -> Iterator[dict]:
        """
        Yield each node (dictionary) for each character in the word
        """
        if not word:
            return
        if not self._case_sensitive:
            word = word.lower()

        node = self._trie_dict
        for idx, char in enumerate(word):
            try:
                node = node[char]
            except KeyError:
                raise WordNotFoundError(
                    f'Not able to locate "{word}" in the Trie Dict. (failed at character "{word[idx]}")')
            yield node

    def get_keyword(self, word: str) -> str:
        """
        Get the clean_word for a given word
        """
        if not self._case_sensitive:
            word = word.lower()
        return self._keywords_dict[word]

    def reset_dict(self) -> None:
        """
        Reset all the keywords and the trie-tree
        """
        self.__init__()

    def __contains__(self, word: str) -> bool:
        """
        Check if we already have the given keyword
        Note that if self._case_sensitive is False it will convert the word to lowercase, and then check...
        """
        if not self._case_sensitive:
            word = word.lower()
        return word in self._keywords_dict

    def __iter__(self) -> Iterator[tuple[str, str]]:
        """
        Yield tuples from self._keywords_dict (tuple(word, clean_word))
        """
        for tup in self._keywords_dict.items():
            yield tup

    def __len__(self) -> int:
        """
        Get the amount of words in the keywords dictionary
        """
        return len(self._keywords_dict)

    def __eq__(self, other) -> bool:
        """
        Check if the trie-tree of another object is the same as its own
        """
        if not isinstance(other, TrieDict) or len(self) != len(other):
            return False
        return self._trie_dict == other._trie_dict

    def __repr__(self) -> str:
        """
        Get the Trie Dictionary
        """
        return f'{__class__.__name__}(case_sensitive={self._case_sensitive})'

    # other ways to add/remove keywords

    def add_keywords_from_iterable(self, keywords: Iterable[str]) -> None:
        for keyword in keywords:
            self.add_keyword(keyword)

    def remove_keywords_from_iterable(self, keywords: Iterable[str]) -> None:
        for keyword in keywords:
            self.remove_keyword(keyword)

    def add_keywords_from_dict(self, keywords_dict: dict[str, str] | dict[str, list[str]]) -> None:
        """
        Add keywords to the trie tree from a dictionary

        The dictionary could be either: {word1: clean_word1, word2: clean_word2, ...} or:
        {clean_word1: [word1, word2, word3], clean_word2: [word1, word2], ...}

        Examples:

        >>> from flashtext2 import KeywordProcessor
        >>> kp = KeywordProcessor()
        >>> kp.add_keywords_from_dict({'Py': 'Python', 'Go': 'Golang'})  # dict[str, str], or:
        >>> d = {
        ...     'Python': ['py', 'python3', 'python2', 'pythonista', 'pythonic'],
        ...     'Trie': ['trie tree', 'trie dict', '']
        ... }
        >>> kp.add_keywords_from_dict(d)
        >>> kp.get_keywords
        {'py': 'Python',
         'go': 'Golang',
         'python3': 'Python',
         'python2': 'Python',
         'pythonista': 'Python',
         'pythonic': 'Python',
         'trie tree': 'Trie',
         'trie dict': 'Trie'}

        :param keywords_dict: dict[str, str] | dict[str, list]
        :return: None
        """
        for key, val in keywords_dict.items():
            if isinstance(val, str):
                self.add_keyword(key, val)

            elif isinstance(val, list):
                for word in val:
                    self.add_keyword(word, key)
            else:
                raise TypeError(f'Expected dict value to be str or list, but found: {type(val)} (dict key: {key})')

    def remove_keywords_from_dict(self, keywords_dict: dict[str, str] | dict[str, list[str]]) -> None:
        for key, val in keywords_dict.items():
            if isinstance(val, str):
                self.remove_keyword(key)

            elif isinstance(val, list):
                for word in val:
                    self.remove_keyword(word)
            else:
                raise TypeError(f'Expected dict value to be str or list, but found: {type(val)} (dict key: {key})')

    def add_keyword_from_file(self, file_path: str, sep: str = '=>',  encoding: str = 'utf-8') -> None:
        with open(file_path, mode='r', encoding=encoding) as f:
            for line in f:
                if sep in line:
                    word, clean_word = line.split(sep)
                    self.add_keyword(word.strip(), clean_word.strip())
                else:
                    self.add_keyword(line.strip())

    # methods to support current flashtext API:
    # these methods are not ideal, and exist only for backwards compatibility

    def add_keywords_from_list(self, keywords: list[str]) -> None:
        self.add_keywords_from_iterable(keywords)

    def remove_keywords_from_list(self, keywords: list[str]) -> None:
        self.remove_keywords_from_iterable(keywords)
