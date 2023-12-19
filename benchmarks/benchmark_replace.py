from __future__ import annotations

import time
import random
import itertools
from typing import TYPE_CHECKING, Iterator

import flashtext
import flashtext2
import pandas as pd

from utils import all_words

N_TESTS = 5


def benchmark() -> Iterator[dict[str, ...]]:
    for i in range(0, 100001, 1000):
        data = {'count': i}

        words = random.sample(all_words, 10_000)
        sentence = ' '.join(words)  # len(story) == 10,000 * 6 = 60,000 chars
        keywords = random.sample(all_words, i)

        # ------ tests --------------------------------------------------------------------------------------
        kp = flashtext.KeywordProcessor()
        kp.add_keywords_from_list(keywords)

        start = time.perf_counter()
        out1 = kp.replace_keywords(sentence)
        data['flashtext'] = time.perf_counter() - start
        del kp  # use only flashtext 2.0 for the next tests

        kp2 = flashtext2.KeywordProcessor()
        kp2.add_keywords(keywords)

        start = time.perf_counter()
        out2 = kp2.replace_keywords(sentence)
        data['flashtext2'] = time.perf_counter() - start
        del kp2
        # ---------------------------------------------------------------------------------------------------

        # to make sure we exhausted the generators if the output is a list
        assert isinstance(out1, str)
        assert isinstance(out2, str)
        assert len(out1) == len(out2), ('Length:', len(out1), len(out2))
        assert out1 == out2

        yield data


def main():
    data = itertools.chain(*(benchmark() for _ in range(N_TESTS)))

    df = pd.DataFrame(data=data)
    avg_df = df.groupby('count').mean()  # this is necessary if N_TESTS > 1
    assert len(avg_df) == len(df) // N_TESTS

    name_color_map = {
        'flashtext (with span-info)': '#1f77b4',
        'flashtext': '#17becf',
        'flashtext2 (with span-info)': '#ff7f0e',
        'flashtext2': '#d62728',
    }
    plt = avg_df.plot.line(
        title='Time For Replacing Keywords',
        xlabel='Word Count',
        ylabel='Seconds',
        color=[name_color_map[col] for col in avg_df.columns],
        grid=True,
    )
    plt.figure.savefig('replace-keywords.png')


if __name__ == '__main__':
    main()
