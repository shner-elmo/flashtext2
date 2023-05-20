from __future__ import annotations


class FlashTextException(Exception):
    """
    Base TrieDict Exception
    """
    pass


class WordNotFoundError(FlashTextException):
    """
    Raised when given word isn't present in the tree data structure
    """
    pass


class MatchingConflictException(FlashTextException):
    """

    """
    def __init__(self, key: str, val1: str, val2: str):
        self.key = key
        self.val1 = val1
        self.val2 = val2

    def __str__(self):
        return f'Duplicate values: {self.key} matches both {self.val1} and {self.val2}'
