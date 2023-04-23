# cython: language_level=3, language=c++

import io
import string
from collections.abc import Mapping as ABC_Mapping, Iterable as ABC_Iterable

cdef set NON_WORD_BOUNDARIES = set(string.digits + string.ascii_letters + '_')
cdef str KEYWORD = '__keyword__'


def convert_trie_to_dict(dict dct, str s = '', dict mapping = None):
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


cdef class KeywordProcessor:
    # these attributes shouldn't be changed after initialization, as they will dictate how the sentences are stored
    # in the trie, and if it's changed after populating the trie, the `extract_keywords` function won't be able to
    # find the keywords in the trie
    cdef:
        readonly str keyword
        readonly bint _case_sensitive
        readonly dict trie
        readonly set non_word_boundaries

    def __cinit__(KeywordProcessor self, bint case_sensitive = False, set non_word_boundaries = None):
        """
        Initialize the Keyword Processor

        If case_sensitive is False, it will convert all the strings to lowercase.

        :param case_sensitive: bool, default False
        """
        self.keyword = KEYWORD
        self._case_sensitive = case_sensitive
        self.trie = {}
        self.non_word_boundaries = non_word_boundaries or NON_WORD_BOUNDARIES

    cpdef dict get_keywords(KeywordProcessor self):
        # explore the trie and extract all the words (this method shouldn't slow down adding keywords,
        # and should be used for debugging)
        return convert_trie_to_dict(self.trie)

    def _split_sentence(KeywordProcessor self, str sentence):
        cdef str word, c
        word = ''
        for c in sentence:
            if c in self.non_word_boundaries:
                word += c
            else:
                if word:  # to avoid adding empty strings
                    yield word
                    word = ''
                yield c
        if word:  # check if there is a word that we haven't added yet
            yield word

    cpdef void add_keyword(KeywordProcessor self, str word, str clean_word = None):
        """
        Add a given keyword to the trie dict

        Examples:
        
        >>> from flashtext_cy import KeywordProcessor
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
        cdef:
            dict node = self.trie
            str chars

        if clean_word is None:
            clean_word = word
        if not self._case_sensitive:
            word = word.lower()

        for chars in self._split_sentence(word):
            node = node.setdefault(chars, {})
        node[self.keyword] = clean_word

    # TODO: test all examples
    cpdef void add_keywords(KeywordProcessor self, words):
        """
        # TODO add examples

        :param words: Iterable[word] or Mapping[word, clean_word] or Mapping[clean_word, Iterable[word]]
        :return:
        """
        cdef:
            dict words_dct
            str word, clean_word
        # cdef words_it

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

    # @overload
    # def extract_keywords(self, sentence: str, span_info: bool = False) -> list[str]:
    #     ...
    #
    # @overload
    # def extract_keywords(self, sentence: str, span_info: Literal[True]) -> list[tuple[str, int, int]]:
    #     ...

    cpdef list extract_keywords(KeywordProcessor self, str sentence, bint span_info = False):
        """
        Extract all the keywords from the given sentence

        If span_info is True it will return a list of tuples containing: (keyword, start_idx, end_idx),
        otherwise it will return a list of keywords.

        Examples:
        
        >>> from flashtext_cy import KeywordProcessor
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
        cdef:
            str kw
            int start, end, _

        if span_info:
            raise NotImplementedError
        return [kw for kw, _, _ in self.extract_keywords_impl(sentence)]

    def extract_keywords_impl(KeywordProcessor self, str sentence):
        if not self._case_sensitive:
            sentence = sentence.lower()

        cdef:
            list words
            tuple last_kw_found
            dict node, trie
            Py_ssize_t n_words
            int n_words_covered, idx
            str word, keyword, kw

        keyword = self.keyword
        node = trie = self.trie
        words = list(self._split_sentence(sentence))
        n_words = len(words)
        # keywords = []
        last_kw_found = ()
        n_words_covered = 0
        idx = 0

        while idx < n_words:
            word = words[idx]

            n_words_covered += 1
            node = node.get(word)
            if node:
                kw = node.get(keyword)
                if kw:
                    last_kw_found = (kw, 0, 0)
            else:
                if last_kw_found:
                    yield last_kw_found
                    # keywords.append(last_kw_found)
                    last_kw_found = ()
                    idx -= 1
                else:
                    idx -= n_words_covered - 1
                node = trie
                n_words_covered = 0
            idx += 1

        # check if there is a keyword that we haven't added yet
        if last_kw_found:
            yield last_kw_found
            # keywords.append(last_kw_found)
        # return keywords

    cpdef str replace_keywords(KeywordProcessor self, str sentence):
        """
        Replace the words with their respective 'clean_word' in the given sentence

        Examples:
        
        >>> from flashtext_cy import KeywordProcessor
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
        # cdef io.StringIO s  # 'io' is not a cimported module
        cdef:
            int start, end, prev_end
            str kw

        s = io.StringIO()
        prev_end = 0
        for kw, start, end in self.extract_keywords(sentence, span_info=True):
            s.write(sentence[prev_end:start] + kw)
            prev_end = end
        # after replacing all the keywords we need to get the text between the last keyword and the end of the sentence
        s.write(sentence[prev_end:])
        return s.getvalue()

    def __eq__(KeywordProcessor self, other):
        return (isinstance(other, KeywordProcessor) and self.non_word_boundaries == other.non_word_boundaries
                and self.get_keywords() == other.get_keywords())

    def __repr__(KeywordProcessor self):
        return repr(self.get_keywords())
