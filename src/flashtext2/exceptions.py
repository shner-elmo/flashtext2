from __future__ import annotations


class FlashTextException(Exception):
    """
    Base TrieDict Exception
    """


class WordNotFoundError(FlashTextException):
    """
    Raised when given word isn't present in the tree data structure
    """
