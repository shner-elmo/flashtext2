# cython: language_level=3, boundscheck=False

cpdef list extract_keywords_iter(str sentence, list words, str keyword, dict trie):
    cdef dict node = trie
    cdef str last_kw_found = ''
    cdef int n_words_covered = 0
    cdef int idx = 0
    cdef str kw
    cdef str word

    cdef list keywords_found = []
    cdef int n_words = len(words)
    while idx < n_words:
        word = words[idx]

        n_words_covered += 1
        node = node.get(word)
        if node:
            kw = node.get(keyword)
            if kw:
                last_kw_found = kw
        else:
            if last_kw_found != '':
                keywords_found.append(last_kw_found)
                last_kw_found = ''
                idx -= 1
            else:
                idx -= n_words_covered - 1
            node = trie
            n_words_covered = 0
        idx += 1
    return keywords_found
