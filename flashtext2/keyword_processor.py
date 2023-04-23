from __future__ import annotations

import io
import string
from typing import Iterable, Mapping, Literal, overload, Iterator
from collections.abc import Mapping as ABC_Mapping, Iterable as ABC_Iterable

NON_WORD_BOUNDARIES = set(string.digits + string.ascii_letters + '_')
KEYWORD = '__keyword__'


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
        if key == KEYWORD:
            mapping[s] = val
        elif isinstance(val, dict):
            convert_trie_to_dict(val, s=s + key, mapping=mapping)
    return mapping


class KeywordProcessor:
    # these attributes shouldn't be changed after initialization, as they will dictate how the sentences are stored
    # in the trie, and if it's changed after populating the trie, the `extract_keywords` function won't be able to
    # find the keywords in the trie
    __slots__ = ('keyword', '_case_sensitive', 'trie', 'non_word_boundaries')

    def __init__(self, case_sensitive: bool = False, non_word_boundaries: set[str] | None = None) -> None:
        """
        Initialize the Keyword Processor

        If case_sensitive is False, it will convert all the strings to lowercase.

        :param case_sensitive: bool, default False
        """
        self.keyword = KEYWORD
        self._case_sensitive = case_sensitive
        self.trie = {}
        self.non_word_boundaries = non_word_boundaries or NON_WORD_BOUNDARIES

    def get_keywords(self) -> dict[str, str]:
        # explore the trie and extract all the words (this method shouldn't slow down adding keywords,
        # and should be used for debugging)
        return convert_trie_to_dict(self.trie)

    def add_keyword(self, word: str, clean_word: str | None = None):
        """
        Add a given keyword to the trie dict

        Examples:
        
        >>> from flashtext2 import KeywordProcessor
        >>> kp = KeywordProcessor()
        >>> kp.add_keyword('C++')
        >>> kp.add_keyword('py', 'Python')
        >>> kp.add_keyword('Py3k', 'Python3')
        >>> kp.get_keywords()
        {'c++': 'C++', 'py': 'Python', 'py3k': 'Python3'}

        :param word:
        :param clean_word:
        :return: None
        """
        if clean_word is None:
            clean_word = word
        if not self._case_sensitive:
            word = word.lower()

        node = self.trie
        for char in word:
            node = node.setdefault(char, {})
        node[self.keyword] = clean_word

    # TODO: test all examples
    def add_keywords(self, words: Iterable[str] | Mapping[str, str] | Mapping[str, Iterable[str]]):
        """
        # TODO add examples

        :param words: Iterable[word] or Mapping[word, clean_word] or Mapping[clean_word, Iterable[word]]
        :return:
        """
        if not isinstance(words, ABC_Mapping):
            words_dct = {w: None for w in words}
        else:
            first_val = next(iter(words.values()))
            if isinstance(first_val, str):
                words_dct = words
            elif isinstance(first_val, ABC_Iterable):
                words_dct = {word: clean_word for clean_word, words_it in words.items() for word in words_it}
            else:  # if the value isn't an Iterable OR Mapping: raise an error
                raise TypeError('words should be one of the following: Iterable[word] or Mapping[word, clean_word] or '
                                'Mapping[clean_word, Iterable[word]]')

        for word, clean_word in words_dct.items():
            self.add_keyword(word, clean_word)

    @overload
    def extract_keywords(self, sentence: str, span_info: Literal[False]) -> list[str]:
        ...

    @overload
    def extract_keywords(self, sentence: str, span_info: Literal[True]) -> list[tuple[str, int, int]]:
        ...

    def extract_keywords(self, sentence: str, span_info: bool = False):
        """
        Extract all the keywords from the given sentence

        If span_info is True it will return a list of tuples containing: (keyword, start_idx, end_idx),
        otherwise it will return a list of keywords.

        Examples:
        
        >>> from flashtext2 import KeywordProcessor
        >>> kp = KeywordProcessor()
        >>> kp.add_keywords({'py': 'Python', 'go': 'Golang', 'hello': 'Hey'})
        >>> s = 'Hello, I love learning Py, aka: Python, and I plan to learn about Go as well.'
        >>> kp.extract_keywords(s)
        ['Hey', 'Python', 'Golang']
        >>> kp.extract_keywords(s, span_info=True)  # not implemented yet
        [('Hey', 0, 5), ('Python', 23, 25), ('Golang', 66, 68)]

        :param sentence: string
        :param span_info: bool, default False
        :return: list of strings or list of tuples
        """
        if span_info:
            raise NotImplementedError
        return [kw for kw, _, _ in self.extract_keywords_impl(sentence)]

    def extract_keywords_impl(self, sentence: str) -> Iterator[str]:
        # if not self._case_sensitive:
        #     sentence = sentence.lower()
        #
        # keyword = self.keyword
        # node = trie = self.trie
        # last_kw_found = ()
        # n_words_covered = 0
        # idx = 0
        # yield 1
        raise NotImplementedError

    def replace_keywords(self, sentence: str) -> str:
        """
        Replace the words with their respective 'clean_word' in the given sentence

        Examples:
        
        >>> from flashtext2 import KeywordProcessor
        >>> kp = KeywordProcessor()
        >>> kp.add_keywords({'py': 'Python', 'go': 'Golang', 'hello': 'Hey'})
        >>> my_str = 'Hello, I love learning Py, aka: Python, and I plan to learn about Go as well.'
        >>> kp.replace_keywords(my_str)
        'Hey, I love learning Python, aka: Python, and I plan to learn about Golang as well.'
        # TODO: add 2nd example with only clean words
        >>> kp = KeywordProcessor()  #
        >>> kp.add_keywords({'py': 'Python', 'go': 'Golang', 'hello': 'Hey'})
        >>> my_str = 'Hello, I love learning Py, aka: Python, and I plan to learn about Go as well.'
        >>> kp.replace_keywords(my_str)
        'Hey, I love learning Python, aka: Python, and I plan to learn about Golang as well.'

        :param sentence: str
        :return: new sentence with the words replaced with their corresponding clean words (if available)
        """

        s = io.StringIO()
        prev_end = 0
        for kw, start, end in self.extract_keywords(sentence, span_info=True):
            s.write(sentence[prev_end:start] + kw)
            prev_end = end
        # after replacing all the keywords we need to get the text between the last keyword and the end of the sentence
        s.write(sentence[prev_end:])
        return s.getvalue()

    def __eq__(self, other) -> bool:
        return (isinstance(other, KeywordProcessor) and self.non_word_boundaries == other.non_word_boundaries
                and self.get_keywords() == other.get_keywords())

    def __repr__(self) -> str:
        return repr(self.get_keywords())
