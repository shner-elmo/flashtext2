from __future__ import annotations

import string
from typing import Iterator, Literal, overload

from .trie_dict import TrieDict


class KeywordProcessor(TrieDict):
    def __init__(self, case_sensitive: bool = False) -> None:
        self.non_word_boundaries: set[str] = set(string.digits + string.ascii_letters + '_')
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
        otherwise it will return a list of keywords

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
        >>> my_str = 'Hello, I love learning Py, aka: Python, and I plan to learn about Go as well. ' \
        '(I can ignore substrings as well, for ex: goal)'
        >>> list(kp.extract_keywords_iter(my_str))
        [('Hey', 0, 5), ('Python', 23, 25), ('Golang', 66, 68)]

        :param sentence: str
        :return: Generator
        """
        if not self._case_sensitive:
            sentence = sentence.lower()

        keyword_key = self.keyword
        trie_dict = self.trie_dict
        non_word_boundaries = self.non_word_boundaries
        sentence_len = len(sentence)
        prev_char: str | None = None

        for idx, char in enumerate(sentence):
            # if prev_char not in [A-Za-z0-9_] AND the next char is in [A-Za-z0-9_]
            if prev_char not in non_word_boundaries and char in non_word_boundaries:
                longest_kw_tup: tuple[str, int, int] | None = None  # (keyword, start_pos, end_pos)

                node = trie_dict
                for i in range(idx, sentence_len):
                    node = node.get(sentence[i])

                    if node is None:
                        break
                    kw = node.get(keyword_key)
                    # if kw AND (it's the last char in the sentence OR the next char is not in [A-Za-z0-9_])
                    if kw and (i == sentence_len - 1 or sentence[i + 1] not in non_word_boundaries):
                        longest_kw_tup = (kw, idx, i + 1)  # the last keyword will automatically be the longest

                if longest_kw_tup:
                    yield longest_kw_tup
            prev_char = char

    def replace_keywords(self, sentence: str) -> str:
        """
        Replace the words with their respective 'clean_word' in the given sentence

        Examples:

        >>> from flashtext2 import KeywordProcessor
        >>> kp = KeywordProcessor()
        >>> kp.add_keywords_from_dict({'py': 'Python', 'go': 'Golang', 'hello': 'Hey'})
        >>> my_str = 'Hello, I love learning Py, aka: Python, and I plan to learn about Go as well. ' \
        '(I can ignore substrings as well, for ex: goal)'
        >>> kp.replace_keywords(my_str)
        'Hey, I love learning Python, aka: Python, and I plan to learn about Golang as well.
        (I can ignore substrings as well, for ex: goal)'

        :param sentence: str
        :return: new sentence with the words replaced
        """
        s = ''
        prev_end = 0
        for kw, start, end in self.extract_keywords_iter(sentence):
            s += sentence[prev_end:start] + kw
            prev_end = end
        # after replacing all the keywords we need to get the text between the last keyword and the end of the sentence
        return s + sentence[prev_end:]
