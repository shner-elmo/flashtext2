from __future__ import annotations

import flashtext
import flashtext2
import pandas as pd

import time
import random
import re
import itertools
import string
from typing import Iterator, TYPE_CHECKING

from utils import all_words  # , pretty_print

if TYPE_CHECKING:
    from flashtext2 import KeywordProcessor


non_word_boundaries_: set[str] = set(string.digits + string.ascii_letters + '_')


def split_sentence(sentence: str) -> Iterator[tuple[bool, str]]:
    for is_word, word in itertools.groupby(sentence, key=non_word_boundaries_.__contains__):
        yield is_word, ''.join(word)


def add_keyword(self: KeywordProcessor, word: str, clean_word: str | None = None) -> None:
    if not clean_word:
        clean_word = word
    if not self._case_sensitive:
        word = word.lower()

    node = self._trie_dict
    for _, word in split_sentence(word):
        node = node.setdefault(word, {})

    node[flashtext2.TrieDict.keyword] = clean_word
    self._keywords_dict[word] = clean_word


def extract_keywords_iter(self: KeywordProcessor, sentence: str) -> Iterator[tuple[str, int, int]]:
    if not self._case_sensitive:
        sentence = sentence.lower()

    keyword_key = self.keyword
    trie_dict = self.trie_dict

    longest_kw_tup = None
    node = trie_dict
    word_len = 0

    idx = 0
    for word in itertools.chain(re.split(self._split_pattern, sentence), ['']):
        idx += len(word)

        node = node.get(word)

        if node is None:
            if longest_kw_tup:
                yield longest_kw_tup

            longest_kw_tup = None
            node = trie_dict
            word_len = 0
            continue
        else:
            word_len += len(word)

        kw = node.get(keyword_key)
        if kw:
            longest_kw_tup = (kw, idx - word_len, idx)


def test() -> list[tuple]:
    lst = []
    # pretty_print('count', 'flashtext', 'flashtext2')
    for i in range(0, 100001, 1000):
        words = random.sample(all_words, 10_000)
        sentence = ' '.join(words)  # len(story) == 10,000 * 6 = 60,000 chars
        keywords = random.sample(all_words, i)

        # ------ tests --------------------------------------------------------------------------------------
        kp = flashtext.KeywordProcessor()
        kp.add_keywords_from_list(keywords)

        start = time.perf_counter()
        out1 = kp.extract_keywords(sentence, span_info=False)
        time1 = time.perf_counter() - start
        del kp  # use only flashtext 2.0 for the next tests

        kp = flashtext2.KeywordProcessor()
        kp.add_keywords_from_list(keywords)

        start = time.perf_counter()
        out2 = kp.extract_keywords(sentence, span_info=False)
        time2 = time.perf_counter() - start
        del kp

        kp = flashtext2.KeywordProcessor()
        for w in keywords:
            add_keyword(self=kp, word=w)

        # print(out2)
        # print(keywords)
        # print(sentence)
        # print()
        # print(kp.get_keywords)
        # print(kp.trie_dict)
        # print([x[0] for x in extract_keywords_iter(kp, sentence)])
        # print('-' * 100)

        start = time.perf_counter()
        out3 = [x[0] for x in extract_keywords_iter(kp, sentence)]
        time3 = time.perf_counter() - start

        # print(time1, time2, time3)
        # ---------------------------------------------------------------------------------------------------

        # to make sure we exhausted the generators if the output is a list
        assert isinstance(out1, list)
        assert isinstance(out2, list)
        assert isinstance(out3, list)
        assert len(out1) == len(out2) == len(out3), ('Length:', len(out1), len(out2), len(out3), out1, out2, out3)
        assert out1 == out2
        assert out2 == out3, (out2, out3)

        # you can uncomment this if you want copy and paste the output in gsheets or excel
        # pretty_print(i, time1, time2)
        lst.append((i, time1, time2, time3))
    return lst


def main():
    def mean(it) -> float:
        return sum(it) / len(it)

    cols = [list(zip(*test())) for _ in range(5)]
    n_cols = len(cols[0])

    new_cols = [[] for _ in range(n_cols)]
    for x in range(5):
        for i in range(n_cols):
            # print([cols[x][i]])
            new_cols[i].append(cols[x][i])

    # get the average of each column
    new_cols = [list(map(mean, zip(*col_grp))) for col_grp in new_cols]

    count, time1, time2, time3 = new_cols
    df = pd.DataFrame({
        'count': count,
        'flashtext': time1,
        'flashtext 2.0': time2,
        'flashtext 2.0 (beta)': time3,
    })
    plt = df.plot.line(title='Time For Extracting Keywords', x='count', xlabel='Word Count',
                       ylabel='Seconds', y=['flashtext', 'flashtext 2.0', 'flashtext 2.0 (beta)'], grid=True)
    plt.figure.savefig('extract-keywords.png')


if __name__ == '__main__':
    main()
