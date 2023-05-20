from __future__ import annotations

import re
from typing import Iterable, Iterator

from .exceptions import WordNotFoundError, MatchingConflictException


class TrieDict:
    __slots__ = ('_case_sensitive', '_trie_dict', '_keywords_dict', 'include_keys')
    keyword = '__keyword__'

    def __init__(self, case_sensitive: bool = False, include_keys = True) -> None:
        self._case_sensitive = case_sensitive  # shouldn't be changed after __init__()
        self._trie_dict = {}
        self.include_keys = include_keys
        self._keywords_dict: dict[str, str] = {}  # dict[word, clean_word]

    @staticmethod
    def split_sentence(sentence: str) -> list[str]:
        """
        Return an iterable that yields parts of the sentence (words, characters, or a mix of both ...)

        Since there are different ways to split the sentence and store it into the trie-dict or to extract its
        components from a string, it's best to have all this code in one place.
        """
        # TODO add self.split_sentence_iter() to take advantage of splitters that are generators
        return list(filter(None, re.split(r'([^a-zA-Z\d])', sentence)))  # remove all the empty strings

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
        >>> kp.get_keywords
        {'c++': 'C++', 'py': 'Python', 'py3k': 'Python3'}

        :param word: str
        :param clean_word: str, optional
        :return: None
        """
        words = {word: clean_word, clean_word: clean_word}
        if not clean_word or self.include_keys is False:
            clean_word = word
            words = {word: clean_word}

        for word, clean_word in words.items():
            if not self._case_sensitive:
                word = word.lower()

            node = self._trie_dict
            for token in self.split_sentence(sentence=word):
                node = node.setdefault(token, {})

            node[TrieDict.keyword] = clean_word
            if word in self._keywords_dict.keys() and self._keywords_dict[word] != clean_word:
                raise MatchingConflictException(word, self._keywords_dict[word], clean_word)
            self._keywords_dict[word] = clean_word

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
                # remove everything from the root of the branch
                del self._trie_dict[self.split_sentence(sentence=word)[0]]
            else:
                # remove all the nodes between the last node that had multiple children and the last letter of our word
                last_multi_node = list(self._node_iterator(word=word))[last_multi_node_idx]
                first_token_to_remove = self.split_sentence(sentence=word)[last_multi_node_idx + 1]
                del last_multi_node[first_token_to_remove]

        del self._keywords_dict[word]

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
                raise WordNotFoundError(f'Not able to locate "{word}" in the Trie Dict. '
                                        f'(failed at character "{list(self.split_sentence(word))[idx]}")')
            yield node

    def get_keyword(self, word: str) -> str | None:
        """
        Get the clean_word for a given word (if it doesn't exist: return None)

        Examples:

        >>> from flashtext2 import KeywordProcessor
        >>> kp = KeywordProcessor()
        >>> kp.add_keyword('py', 'Python')
        >>> kp.get_keyword('py')
        'Python'
        >>> kp.get_keyword('non-existent-word')  # output: None

        :param word: str
        :return: its respective clean word
        """
        if not self._case_sensitive:
            word = word.lower()
        return self._keywords_dict.get(word)

    def __getitem__(self, word: str) -> str | None:
        """
        Get the clean_word for a given word (if it doesn't exist: return None)
        """
        return self.get_keyword(word)

    def __setitem__(self, word: str, clean_word: str) -> None:
        """
        Add a given keyword to the trie dict
        """
        self.add_keyword(word, clean_word)

    def __delitem__(self, word) -> None:
        """
        Remove a keyword from the trie dict
        """
        self.remove_keyword(word)

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
        yield from self._keywords_dict.items()

    def __len__(self) -> int:
        """
        Get the amount of words in the trie dict
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

    def remove_keywords_from_dict(self, keywords_dict: dict[str, str] | dict[str, list[str]]) -> None:
        """
        Add keywords from a text file

        Examples:

        >>> from flashtext2 import KeywordProcessor
        >>> kp = KeywordProcessor()
        >>> d = {'Py': 'Python', 'Go': 'Golang'}
        >>> kp.add_keywords_from_dict(d)
        >>> len(kp)  # amount of keywords in the trie dict
        2
        >>> kp.remove_keywords_from_dict(d)
        >>> len(kp)
        0
        >>> d = {
        ...     'Python': ['py', 'python3', 'python2', 'pythonista', 'pythonic'],  # dict[str, list[str]]
        ...     'Trie': ['trie tree', 'trie dict']
        ... }
        >>> kp.add_keywords_from_dict(d)
        >>> kp.remove_keywords_from_dict(d)
        >>> len(kp)
        0

        :param keywords_dict: dict[word, clean_word] or dict[clean_word, list[word]]
        :return:
        """
        for key, val in keywords_dict.items():
            if isinstance(val, str):
                self.remove_keyword(key)

            elif isinstance(val, list):
                for word in val:
                    self.remove_keyword(word)
            else:
                raise TypeError(
                    f'Expected dict value to be str or list, but found: {type(val).__name__} (dict key: {key})')

    def add_keyword_from_file(self, file_path: str, sep: str = '=>',  encoding: str = 'utf-8') -> None:
        """
        Add keywords from a text file

        Examples:

        # keywords.txt
        java_2e => java
        java programing=>java
        product management   =>product management
        product management techniques=>   product management
        java
        python
        c++

        >>> from flashtext2 import KeywordProcessor
        >>> kp = KeywordProcessor()
        >>> kp.add_keyword_from_file('keywords.txt')
        >>> kp.get_keywords
        {'java_2e': 'java',
         'java programing': 'java',
         'product management': 'product management',
         'product management techniques': 'product management',
         'java': 'java',
         'python': 'python',
         'c++': 'c++'}

        :param file_path: path to the text file
        :param sep: string used to seperate the word and clean_word in each line, default '=>'
        :param encoding: default 'utf-8'
        :return: None
        """
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
        """
        Add keywords from a list

        :param keywords: list of words
        :return: None
        :raises TypeError: if keywords is not a list
        """
        if not isinstance(keywords, list):
            raise TypeError(f"Expected type list for param 'keywords', but got {type(keywords).__name__}")
        self.add_keywords_from_iter(keywords)

    def remove_keywords_from_list(self, keywords: list[str]) -> None:
        """
        Remove keywords from a list

        :param keywords: list of words
        :return: None
        :raises TypeError: if keywords is not a list
        """
        if not isinstance(keywords, list):
            raise TypeError(f"Expected type list for param 'keywords', but got {type(keywords).__name__}")
        self.remove_keywords_from_iter(keywords)

    def get_all_keywords(self) -> dict[str, str]:
        """
        Get the dictionary containing all the words and their corresponding clean words (dict[word, clean_word])
        """
        return self.get_keywords
