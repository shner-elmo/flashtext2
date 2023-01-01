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
