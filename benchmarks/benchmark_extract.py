from __future__ import annotations

import sys
import time
import random
import itertools
from typing import TYPE_CHECKING, Iterator

import flashtext
import flashtext2
import pandas as pd

from utils import all_words

if TYPE_CHECKING:
    from flashtext2 import KeywordProcessor

N_TESTS = 5


# TODO; use regular text with human selected keywords.
def benchmark() -> Iterator[dict[str, ...]]:
    for i in range(0, 100001, 1000):
        data = {'count': i}
        output = []

        words = random.sample(all_words, 10_000)
        sentence = ' '.join(words)  # len(story) == 10,000 * 6 = 60,000 chars
        keywords = random.sample(all_words, i)

        # call this function to cache the regex compilation
        kp = flashtext2.KeywordProcessor()
        kp.add_keywords(['abcd'])
        kp.extract_keywords('abcd abcd')
        # ------ tests --------------------------------------------------------------------------------------

        kp = flashtext.KeywordProcessor()
        kp.add_keywords_from_list(keywords)

        start = time.perf_counter()
        out = kp.extract_keywords(sentence, span_info=True)
        data['flashtext (with span-info)'] = time.perf_counter() - start
        output.append(out)

        start = time.perf_counter()
        out = kp.extract_keywords(sentence, span_info=False)
        data['flashtext'] = time.perf_counter() - start
        output.append(out)
        del kp

        kp2 = flashtext2.KeywordProcessor()
        kp2.add_keywords(keywords)

        start = time.perf_counter()
        out = kp2.extract_keywords_with_span(sentence)
        data['flashtext2 (with span-info)'] = time.perf_counter() - start
        output.append(out)

        start = time.perf_counter()
        out = kp2.extract_keywords(sentence)
        data['flashtext2'] = time.perf_counter() - start
        output.append(out)
        del kp2

        # to make sure we exhausted the generators
        for x in output:
            assert isinstance(x, list), 'Iterator is not exhausted.'

        # compare span_info True with True, and False with False.
        assert output[0] == output[2], (output[0], output[2])
        assert output[1] == output[3], (output[1], output[3])

        yield data


def main():
    name = sys.argv[1]
    print(f'Benchmark name: {name!r}')
    assert '/' not in name  # then it will consider everything before it a directory name

    data = itertools.chain(*(benchmark() for _ in range(N_TESTS)))

    df = pd.DataFrame(data=data)
    df.to_csv(f'{name}.csv')
    avg_df = df.groupby('count').mean()  # this is necessary if N_TESTS > 1
    assert len(avg_df) == len(df) // N_TESTS

    name_color_map = {
        'flashtext (with span-info)': '#1f77b4',
        'flashtext': '#17becf',
        'flashtext2 (with span-info)': '#ff7f0e',
        'flashtext2': '#d62728',
    }
    plt = avg_df.plot.line(
        title=f'Time For Extracting Keywords ({name})',
        xlabel='Word Count',
        ylabel='Seconds',
        color=[name_color_map[col] for col in avg_df.columns],
        grid=True,
    )
    plt.figure.savefig(f'extract-keywords-{name}.png')


if __name__ == '__main__':
    main()
