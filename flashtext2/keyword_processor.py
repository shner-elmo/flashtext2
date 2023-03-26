from __future__ import annotations

import io
from typing import Iterator, Literal, overload

from .trie_dict import TrieDict


class KeywordProcessor(TrieDict):
    def __init__(self, case_sensitive: bool = False) -> None:
        """
        Initialize the Keyword Processor

        If case_sensitive is False, it will convert all the strings to lowercase.

        :param case_sensitive: bool, default False
        """
        super().__init__(case_sensitive)

    @overload
    def extract_keywords(self, sentence: str, span_info: bool = False) -> list[str]:
        ...

    @overload
    def extract_keywords(self, sentence: str, span_info: Literal[True]) -> list[tuple[str, int, int]]:
        ...

    def extract_keywords(self, sentence: str, span_info: bool = False) -> list[str] | list[tuple[str, int, int]]:
        """
        Extract all the keywords from the given sentence

        If span_info is True it will return a list of tuples containing: (keyword, start_idx, end_idx),
        otherwise it will return a list of keywords.

        Examples:

        >>> from flashtext2 import KeywordProcessor
        >>> kp = KeywordProcessor()
        >>> kp.add_keywords_from_dict({'py': 'Python', 'go': 'Golang', 'hello': 'Hey'})
        >>> s = 'Hello, I love learning Py, aka: Python, and I plan to learn about Go as well.'
        >>> kp.extract_keywords(s)
        ['Hey', 'Python', 'Golang']
        >>> kp.extract_keywords(s, span_info=True)
        [('Hey', 0, 5), ('Python', 23, 25), ('Golang', 66, 68)]

        :param sentence: str
        :param span_info: bool, default False
        :return: list of strings or list of tuples
        """
        if span_info:
            return list(self.extract_keywords_iter(sentence))
        return [tup[0] for tup in self.extract_keywords_iter(sentence)]

    def extract_keywords_iter(self, sentence: str) -> Iterator[tuple[str, int, int]]:
        """
        Get a generator that yields the keywords and their start/end position as a tuple (keyword, start_idx, end_idx)

        Examples:

        >>> from flashtext2 import KeywordProcessor
        >>> kp = KeywordProcessor()
        >>> kp.add_keywords_from_dict({'py': 'Python', 'go': 'Golang', 'hello': 'Hey'})
        >>> my_str = 'Hello, I love learning Py, aka: Python, and I plan to learn about Go as well.'
        >>> list(kp.extract_keywords_iter(my_str))
        [('Hey', 0, 5), ('Python', 23, 25), ('Golang', 66, 68)]

        :param sentence: str
        :return: Generator
        """

    def replace_keywords(self, sentence: str) -> str:
        """
        Replace the words with their respective 'clean_word' in the given sentence

        Examples:

        >>> from flashtext2 import KeywordProcessor
        >>> kp = KeywordProcessor()
        >>> kp.add_keywords_from_dict({'py': 'Python', 'go': 'Golang', 'hello': 'Hey'})
        >>> my_str = 'Hello, I love learning Py, aka: Python, and I plan to learn about Go as well.'
        >>> kp.replace_keywords(my_str)
        'Hey, I love learning Python, aka: Python, and I plan to learn about Golang as well.'

        :param sentence: str
        :return: new sentence with the words replaced
        """
        s = io.StringIO()
        prev_end = 0
        for kw, start, end in self.extract_keywords_iter(sentence):
            # s += sentence[prev_end:start] + kw
            s.write(sentence[prev_end:start] + kw)
            prev_end = end
        # after replacing all the keywords we need to get the text between the last keyword and the end of the sentence
        s.write(sentence[prev_end:])
        return s.getvalue()
