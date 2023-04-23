from __future__ import annotations

import re
import time
import string
import itertools
from typing import Iterator

import requests
import regex

import cy_split  # .pyx file

# @ cy_split.pyx:
# # cython: language_level=3
#
# import string
#
# cdef set non_word_boundaries = set(string.digits + string.ascii_letters + '_')
#
#
#
# cdef class SplitSentence:
#     cdef readonly str sentence
#     cdef readonly str word
#     cdef readonly str c
#     cdef readonly int idx
#
#     def __cinit__(SplitSentence self, str sentence):
#         self.sentence = sentence
#         self.idx = -1
#         self.word = ''
#         self.c = None
#
#     def __iter__(SplitSentence self):
#         return self
#
#     def __next__(SplitSentence self):
#         cdef str c, word
#
#         c = self.c
#         if c:
#             self.c = None
#             return c
#
#         while self.idx + 1 < len(self.sentence):
#             self.idx += 1
#             c = self.sentence[self.idx]
#             if c in non_word_boundaries:
#                 self.word += c
#             else:
#                 word = self.word
#                 if word:
#                     self.word = ''
#                     self.c = c
#                     return word
#                 else:
#                     return c
#
#         word = self.word
#         if word:
#             self.word = ''
#             return word
#         raise StopIteration
#
#
# def split_sentence(str sentence):
#     cdef str word, c
#     word = ''
#     for c in sentence:
#         if c in non_word_boundaries:
#             word += c
#         else:
#             if word:  # to avoid adding empty strings
#                 yield word
#                 word = ''
#             yield c
#     if word:  # check if there is a word that we haven't added yet
#         yield word
#

split_pattern = re.compile(r'([^a-zA-Z\d])')
split_pattern_regex = regex.compile(r'([^a-zA-Z\d])')
non_word_boundaries = set(string.digits + string.ascii_letters + '_')


def split_re(sentence: str) -> list[str]:
    return list(filter(None, split_pattern.split(sentence)))


def split_regex(sentence: str) -> list[str]:
    return list(filter(None, split_pattern_regex.split(sentence)))


def _split_python(sentence: str) -> Iterator[str]:
    word = ''
    for c in sentence:
        if c in non_word_boundaries:
            word += c
        else:
            if word:  # to avoid adding empty strings
                yield word
                word = ''
            yield c
    if word:  # check if there is a word that we haven't added yet
        yield word


def split_python(sentence: str) -> Iterator[str]:
    return list(_split_python(sentence))


def split_cython(sentence: str) -> list[str]:
    return list(cy_split.split_sentence(sentence))


def split_cython_class(sentence: str) -> list[str]:
    return list(cy_split.SplitSentence(sentence))


def all_equal(iterable, predicate=None) -> bool:
    """
    Returns True if all the elements are equal to each other
    """
    g = itertools.groupby(iterable, predicate)
    return next(g, True) and not next(g, False)


def main(times_n: int):
    r = requests.get('https://en.wikipedia.org/w/api.php?action=query&format=json&titles=Hannibal&prop=extracts'
                     '&exintro&explaintext&exsectionformat=raw')
    sentence: str = next(iter(r.json()['query']['pages'].values()))['extract'] * times_n

    print(f'{len(sentence)=}')

    d = {}
    for func in [split_re, split_regex, split_python, split_cython, split_cython_class]:
        start = time.perf_counter()
        out = func(sentence)
        d[func.__name__] = out
        print(f'{func.__name__} - {time.perf_counter() - start:f}')

    print('All equal:', all_equal(d.values()))
    print('All equal len:', all_equal(d.values(), predicate=len))
    # for func, out in d.items():
    #     print(func, len(out), out[:1000])


if __name__ == '__main__':
    main(1000)
    main(10000)
    main(100000)
