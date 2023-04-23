from __future__ import annotations

import string
from typing import Iterator

non_word_boundaries = set(string.digits + string.ascii_letters + '_')


class SplitSentence:
    def __init__(self, sentence: str):
        self.sentence = sentence
        self.idx = -1
        self.word = ''
        self.c: str | None = None

    def __iter__(self) -> SplitSentence:
        return self

    def __next__(self) -> str:
        if (c := self.c) is not None:
            self.c = None
            return c
        while self.idx + 1 < len(self.sentence):
            self.idx += 1
            c = self.sentence[self.idx]
            if c in non_word_boundaries:
                self.word += c
            else:
                if word := self.word:
                    self.word = ''
                    self.c = c
                    return word
                else:
                    return c

        if word := self.word:
            self.word = ''
            return word
        raise StopIteration


def split_sentence(sentence: str) -> Iterator[str]:
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


def main():
    s = 'Hello, I love learning Py, aka: Python, and I plan to learn about Go as well. golang'

    out = list(split_sentence(s))
    print(out)

    out = list(SplitSentence(s))
    print(out)


def test():
    s = 'Hello, I love learning Python, and I plan to learn about Go as well. golang'
    assert list(split_sentence(s)) == list(SplitSentence(s))

    s = 'Hello, I love learning Python, and I plan to learn about Go as well. golang.'
    assert list(split_sentence(s)) == list(SplitSentence(s))

    s = 'Hello, I love learning Python, and I plan to learn about Go as well. golang '
    assert list(split_sentence(s)) == list(SplitSentence(s))

    s = 'Hello, I love learning Python, and I plan to learn about Go as well. golang    '
    assert list(split_sentence(s)) == list(SplitSentence(s))

    s = 'Hello, I love learning Python, and I plan to learn about Go as well. golang    ...  .'
    assert list(split_sentence(s)) == list(SplitSentence(s))


if __name__ == '__main__':
    main()
    test()
