import string
import random


__all__ = [
    'pretty_print',
    'get_word',
    'all_words',
]


def pretty_print(*args, sep: str = '\t', ljust: int = 10) -> None:
    s = sep.join([f'{x:f}'.ljust(ljust) if isinstance(x, float) else str(x).ljust(ljust) for x in args])
    print(s)


def get_word(length: int) -> str:
    # generate a random word of given length
    return ''.join([random.choice(string.ascii_lowercase) for _ in range(length)])


# generate a list of 100K words of randomly chosen size
all_words = [get_word(length=random.choice([3, 4, 5, 6, 7, 8])) for _ in range(100_000)]
