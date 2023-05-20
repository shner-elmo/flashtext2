from __future__ import annotations

from typing import Iterator, Literal, overload

from .trie_dict import TrieDict


class KeywordProcessor(TrieDict):
    def __init__(self, case_sensitive: bool = False, include_keys = True) -> None:
        """
        Initialize the Keyword Processor

        If case_sensitive is False, it will convert all the strings to lowercase.

        :param case_sensitive: bool, default False
        """
        super().__init__(case_sensitive, include_keys)

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
        if not self._case_sensitive:
            sentence = sentence.lower()

        words: list[str] = self.split_sentence(sentence) + ['']
        lst_len: list[int] = list(map(len, words))  # cache the len() of each word
        keyword = self.keyword
        trie = self.trie_dict
        node = trie

        last_kw_found: str | None = None
        last_kw_found_idx: tuple[int, int] | None = None
        last_start_span: tuple[int, int] | None = None
        n_words_covered = 0
        idx = 0
        while idx < len(words):
            word = words[idx]

            n_words_covered += 1
            node = node.get(word)
            if node:
                kw = node.get(keyword)
                if kw:
                    last_kw_found = kw
                    last_kw_found_idx = (idx, n_words_covered)
            else:
                if last_kw_found is not None:
                    kw_end_idx, kw_n_covered = last_kw_found_idx
                    start_span_idx = kw_end_idx - kw_n_covered + 1

                    if last_start_span is None:
                        start_span = sum(lst_len[:start_span_idx])
                    else:
                        start_span = last_start_span[1] + sum(lst_len[last_start_span[0]:start_span_idx])
                    last_start_span = start_span_idx, start_span  # cache the len() for the given slice for next time

                    yield last_kw_found, start_span, start_span + sum(
                        lst_len[start_span_idx:start_span_idx + kw_n_covered])
                    last_kw_found = None
                    idx -= 1
                else:
                    idx -= n_words_covered - 1
                node = trie
                n_words_covered = 0
            idx += 1

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
        s = ''
        prev_end = 0
        for kw, start, end in self.extract_keywords_iter(sentence):
            s += sentence[prev_end:start] + kw
            prev_end = end
        # after replacing all the keywords we need to get the text between the last keyword and the end of the sentence
        return s + sentence[prev_end:]
