from __future__ import annotations

import flashtext
import flashtext2
import pandas as pd

import time
import random

from utils import all_words  # , pretty_print


def test() -> list[tuple]:
    lst = []
    # pretty_print('count', 'flashtext', 'flashtext2')
    for i in range(0, 20001, 1000):
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
        # ---------------------------------------------------------------------------------------------------

        # to make sure we exhausted the generators if the output is a list
        assert isinstance(out1, list)
        assert isinstance(out2, list)
        assert len(out1) == len(out2), ('Length:', len(out1), len(out2))
        assert out1 == out2  # TODO use sorted()?

        # you can uncomment this if you want copy and paste the output in gsheets or excel
        # pretty_print(i, time1, time2)
        lst.append((i, time1, time2))
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

    count, time1, time2 = new_cols
    df = pd.DataFrame({
        'count': count,
        'flashtext': time1,
        'flashtext 2.0': time2,
    })
    plt = df.plot.line(title='Time For Extracting Keywords', x='count', xlabel='Word Count',
                       ylabel='Seconds', y=['flashtext', 'flashtext 2.0'])
    plt.figure.savefig('extract-keywords.png')


if __name__ == '__main__':
    main()
