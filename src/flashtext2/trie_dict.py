from __future__ import annotations

import re
from typing import Iterable, Iterator

from flashtext2.utils import convert_trie_to_dict
from flashtext2.exceptions import WordNotFoundError

RE_SPLIT_PATTERN = re.compile(r'([^a-zA-Z\d])')


class TrieDict:
    __slots__ = ('_case_sensitive', '_trie_dict')

    def __init__(self, case_sensitive: bool = False) -> None:
        """
        TODO: complete

        :param case_sensitive:
        """
        self._case_sensitive = case_sensitive  # shouldn't be changed after __init__()
        self._trie_dict = {}

    # TODO: make sure that there are no issues converting this to an iterator instead
    @staticmethod
    def split_sentence(sentence: str) -> Iterator[str]:
        """
        Return an iterable that yields parts of the sentence (words, characters, or a mix of both ...)

        Since there are different ways to split the sentence and store it into the trie-dict or to extract its
        components from a string, it's best to have all this code in one place.
        """
        # filter to remove all the empty strings
        return filter(None, RE_SPLIT_PATTERN.split(sentence))

    @property
    def trie_dict(self) -> dict:
        """
        Get the dictionary containing the trie tree
        """
        return self._trie_dict

    def get_keywords(self) -> dict[str, str]:
        """
        Get the dictionary containing all the words and their corresponding clean words
        """
        return convert_trie_to_dict(dct=self._trie_dict)

    def add_keyword(self, word: str, clean_word: str | None = None) -> None:
        """
        Add a given keyword to the trie dict

        Note that you can only have one 'clean_word' per 'word', so if you add:
        `kp.add_keyword(word='py', clean_word='python')` and then do:
        `kp.add_keyword(word='py', clean_word='python3')`, then it will simply overwrite the clean_word,
        `print(kp.get_keywords)`  # output: {'py': 'python3'}.

        Examples:

        >>> from flashtext2 import KeywordProcessor
        >>> kp = KeywordProcessor()
        >>> kp.add_keyword('C++')
        >>> kp.add_keyword('py', 'Python')
        >>> kp.add_keyword('Py3k', 'Python3')
        >>> kp.get_keywords()
        {'c++': 'C++', 'py': 'Python', 'py3k': 'Python3'}

        :param word: str
        :param clean_word: str, optional
        :return: None
        """
        if not clean_word:
            clean_word = word
        if not self._case_sensitive:
            word = word.lower()

        node = self._trie_dict
        for token in self.split_sentence(sentence=word):
            node = node.setdefault(token, {})

        node[True] = clean_word

    def remove_keyword(self, word: str) -> None:
        """
        Remove a keyword from the trie dict

        Examples:
        >>> from flashtext2 import KeywordProcessor
        >>> kp = KeywordProcessor()
        >>> kp.add_keyword('py', 'Python')
        >>> kp.add_keyword('Py3k', 'Python3')
        >>> kp.get_keywords
        {'py': 'Python', 'py3k': 'Python3'}

        >>> kp.remove_keyword('Py3k')
        >>> kp.get_keywords
        {'py': 'Python'}
        >>> kp.remove_keyword('Py')
        >>> kp.get_keywords
        {}
        >>> kp.trie_dict
        {}

        :param word: str
        :return: None
        :raises WordNotFoundError: if the word is not present in the trie dict
        """
        if not self._case_sensitive:
            word = word.lower()

        # TODO: make sure were removing a valid word (and not corrupting other data)

        # the index of the node that contains multiple children
        last_multi_node_idx = None
        for idx, node in enumerate(self._node_iterator(word)):
            if len(node) > 1:  # node either has children or is a keyword
                last_multi_node_idx = idx
        # noinspection PyUnboundLocalVariable
        del node[True]

        if len(node) == 0:  # if last node has no children we can safely delete prior nodes
            if last_multi_node_idx is None:
                # remove everything from the root of the branch
                del self._trie_dict[self.split_sentence(sentence=word)[0]]
            else:
                # TODO: optimize - use islice() instead of list()
                # remove all the nodes between the last node that had multiple children and the last letter of our word
                last_multi_node = list(self._node_iterator(word=word))[last_multi_node_idx]
                first_token_to_remove = list(self.split_sentence(sentence=word))[last_multi_node_idx + 1]
                del last_multi_node[first_token_to_remove]

    def _node_iterator(self, word: str) -> Iterator[dict]:
        """
        A helper function that yields each node (dictionary) for each token from the given word

        :param word: str
        :return: None
        :raises WordNotFoundError: if the word is not present in the trie dict
        """
        if not word:
            return
        if not self._case_sensitive:
            word = word.lower()

        node = self._trie_dict
        for idx, token in enumerate(self.split_sentence(word)):
            try:
                node = node[token]
            except KeyError:
                raise WordNotFoundError(
                    f'Not able to locate "{word}" in the Trie Dict. '
                    f'(failed at token: "{token}")'
                )
            yield node

    def __eq__(self, other) -> bool:
        """
        Check for equality (it must have the same exact words to be equal)
        """
        return isinstance(other, TrieDict) and other.trie_dict == self.trie_dict

    def __repr__(self) -> str:
        """
        Get the repr
        """
        return f'{__class__.__name__}(case_sensitive={self._case_sensitive!r})'

    # other ways to add/remove keywords
    def add_keywords_from_iter(self, keywords: Iterable[str]) -> None:
        """
        Add keywords from an iterable (list, tuple, set, generator, etc.)

        Examples:

        >>> from flashtext2 import KeywordProcessor
        >>> kp = KeywordProcessor()
        >>> kp.add_keywords_from_iter(['py', 'python', 'go', 'love', 'java'])
        >>> kp.get_keywords
        {'py': 'py', 'python': 'python', 'go': 'go', 'love': 'love', 'java': 'java'}
        >>> s = 'Hello, I love learning Py, aka: Python, and I plan to learn about Go as well.'
        >>> kp.extract_keywords(s)
        ['love', 'py', 'python', 'go']

        :param keywords: iterable of strings/words
        :return: None
        """
        for keyword in keywords:
            self.add_keyword(keyword)

    def remove_keywords_from_iter(self, keywords: Iterable[str]) -> None:
        """
        Remove keywords from an iterable (list, tuple, set, generator, etc.)

        Examples:

        >>> from flashtext2 import KeywordProcessor
        >>> kp = KeywordProcessor()
        >>> words = ['py', 'python', 'go', 'love', 'java']
        >>> kp.add_keywords_from_iter(words)
        >>> kp.get_keywords
        {'py': 'py', 'python': 'python', 'go': 'go', 'love': 'love', 'java': 'java'}
        >>> kp.remove_keywords_from_iter(words)
        >>> kp.get_keywords
        {}

        :param keywords: iterable of strings/words
        :return: None
        """
        for keyword in keywords:
            self.remove_keyword(keyword)

    # TODO: remove this counter-intuitive method for adding keywords
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
        ...     'Trie': ['trie tree', 'trie dict']
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
         >>> s = 'A trie dict can be very powerful for storing text in Py or Go'
         >>> kp.replace_keywords(s)
         'A Trie can be very powerful for storing text in Python or Golang'

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
                raise TypeError(
                    f'Expected dict value to be str or list, but found: {type(val).__name__} (dict key: {key})')
