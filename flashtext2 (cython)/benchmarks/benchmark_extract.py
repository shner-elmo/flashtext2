from __future__ import annotations

import flashtext
import flashtext2
import flashtext_cy

import random
from typing import TYPE_CHECKING

import pandas as pd
from stopwatch import Stopwatch

from utils import all_words  # , pretty_print

if TYPE_CHECKING:
    from flashtext_cy import KeywordProcessor


def test() -> list[tuple]:
    lst = []
    # pretty_print('count', 'flashtext', 'flashtext2')
    for i in range(0, 100001, 1000):
        words = random.sample(all_words, 10_000)
        sentence = ' '.join(words)  # len(story) == 10,000 * 6 = 60,000 chars
        keywords = random.sample(all_words, i)

        # flashtext2.KeywordProcessor.split_sentence('abc d ef')  # call the function to cache the regex compilation
        # ------ tests --------------------------------------------------------------------------------------
        kp = flashtext.KeywordProcessor()
        kp.add_keywords_from_list(keywords)
        with Stopwatch() as sw:
            out1 = kp.extract_keywords(sentence, span_info=False)
            time1 = sw.time_elapsed
        del kp

        kp = flashtext2.KeywordProcessor()
        kp.add_keywords_from_list(keywords)
        with Stopwatch() as sw:
            out2 = kp.extract_keywords(sentence, span_info=False)
            time2 = sw.time_elapsed
        del kp

        kp = flashtext_cy.KeywordProcessor()
        kp.add_keywords(keywords)
        with Stopwatch() as sw:
            out3 = kp.extract_keywords(sentence, span_info=False)
            time3 = sw.time_elapsed
        del kp

        # print(time1, time2, time3)
        # ---------------------------------------------------------------------------------------------------

        # to make sure we exhausted the generators
        assert isinstance(out1, list)
        assert isinstance(out2, list)
        assert isinstance(out3, list)
        # assert isinstance(out3, list)
        assert len(out1) == len(out2), ('Length:', len(out1), len(out2), out1, out2)
        assert len(out2) == len(out3), ('Length:', len(out2), len(out3), out2, out3)
        assert out1 == out2, (out1, out2)
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
        'flashtext 2.0 (Cython)': time3,
    })
    plt = df.plot.line(title='Time For Extracting Keywords', x='count', xlabel='Word Count',
                       ylabel='Seconds', y=['flashtext', 'flashtext 2.0', 'flashtext 2.0 (Cython)'], grid=True)
    plt.figure.savefig('extract-keywords.png')


if __name__ == '__main__':
    main()
