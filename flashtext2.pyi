from typing import Optional, Iterable


class KeywordProcessor:
    case_sensitive: bool
    def __init__(self, case_sensitive: bool) -> None: ...
    def __len__(self) -> int: ...
    def __repr__(self) -> str: ...
    def add_keyword(self, word: str, clean_word: Optional[str] = None) -> None: ...
    def add_keywords_from_iter(self, words: Iterable[str]) -> None: ...
    def add_keywords_with_clean_word_from_iter(self, words: Iterable[tuple[str, str]]) -> None: ...
    def extract_keywords(self, text: str) -> list[str]: ...
    def extract_keywords_with_span(self, text: str) -> list[tuple[str, int, int]]: ...
    def replace_keywords(self, text: str) -> str: ...
