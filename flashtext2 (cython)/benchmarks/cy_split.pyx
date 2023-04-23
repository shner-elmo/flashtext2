# cython: language=c++
# , language_level=3
#
## language_level=3
# ###,

from libcpp.vector cimport vector
from libcpp.set cimport set as cpp_set

# cdef set non_word_boundaries = set(string.digits + string.ascii_letters + '_')


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
from libcpp.vector cimport vector
from libcpp.set cimport set as cpp_set


cdef vector[char] _split_sentence_impl(char *sentence, Py_ssize_t n_chars) except *:
    cdef:
        vector vec[char] # = []
        cpp_set[char] non_word_boundaries
        # char c
        int start = -1
        int idx = -1
    non_word_boundaries.insert('0')
    non_word_boundaries.insert('1')
    non_word_boundaries.insert('2')
    non_word_boundaries.insert('3')
    non_word_boundaries.insert('4')
    non_word_boundaries.insert('5')
    non_word_boundaries.insert('6')
    non_word_boundaries.insert('7')
    non_word_boundaries.insert('8')
    non_word_boundaries.insert('9')
    non_word_boundaries.insert('a')
    non_word_boundaries.insert('b')
    non_word_boundaries.insert('c')
    non_word_boundaries.insert('d')
    non_word_boundaries.insert('e')
    non_word_boundaries.insert('f')
    non_word_boundaries.insert('g')
    non_word_boundaries.insert('h')
    non_word_boundaries.insert('i')
    non_word_boundaries.insert('j')
    non_word_boundaries.insert('k')
    non_word_boundaries.insert('l')
    non_word_boundaries.insert('m')
    non_word_boundaries.insert('n')
    non_word_boundaries.insert('o')
    non_word_boundaries.insert('p')
    non_word_boundaries.insert('q')
    non_word_boundaries.insert('r')
    non_word_boundaries.insert('s')
    non_word_boundaries.insert('t')
    non_word_boundaries.insert('u')
    non_word_boundaries.insert('v')
    non_word_boundaries.insert('w')
    non_word_boundaries.insert('x')
    non_word_boundaries.insert('y')
    non_word_boundaries.insert('z')
    non_word_boundaries.insert('A')
    non_word_boundaries.insert('B')
    non_word_boundaries.insert('C')
    non_word_boundaries.insert('D')
    non_word_boundaries.insert('E')
    non_word_boundaries.insert('F')
    non_word_boundaries.insert('G')
    non_word_boundaries.insert('H')
    non_word_boundaries.insert('I')
    non_word_boundaries.insert('J')
    non_word_boundaries.insert('K')
    non_word_boundaries.insert('L')
    non_word_boundaries.insert('M')
    non_word_boundaries.insert('N')
    non_word_boundaries.insert('O')
    non_word_boundaries.insert('P')
    non_word_boundaries.insert('Q')
    non_word_boundaries.insert('R')
    non_word_boundaries.insert('S')
    non_word_boundaries.insert('T')
    non_word_boundaries.insert('U')
    non_word_boundaries.insert('V')
    non_word_boundaries.insert('W')
    non_word_boundaries.insert('X')
    non_word_boundaries.insert('Y')
    non_word_boundaries.insert('Z')
    non_word_boundaries.insert('_')

    for c in sentence:
        idx += 1
        if non_word_boundaries.count(c) == 0:
            if start != -1:
                vec.push_back(sentence[start:idx])
            vec.push_back(sentence[idx])
            start = -1
        else:
            if start == -1:
                start = idx
    if start != -1:  # check if there is a word that we haven't added yet
        vec.push_back(sentence[idx])
    return vec

def split_sentence(str sentence, str encoding = 'utf8'):
    cdef:
        vector[char] out
        bytes py_bytes = sentence.encode()
        char *c_str = py_bytes  # gotta pass a reference to a Python object and not the object itself
    out = _split_sentence_impl(c_str, len(sentence))
    return [chr(x) for x in out]

#     word = ''
#     for c in sentence:
#         if c in non_word_boundaries:
#             word += c
#         else:
#             if word:  # to avoid adding empty strings
#                 vec.push_back(word)
#                 word = ''
#             vec.push_back(c)
#     if word:  # check if there is a word that we haven't added yet
#         vec.push_back(word)