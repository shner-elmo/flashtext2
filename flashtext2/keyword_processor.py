from __future__ import annotations

from typing import Union, Literal, overload

from .trie_dict import TrieDict
from .utils import normalize_parameter


class KeywordProcessor(TrieDict):

    @overload
    def extract_keywords(self, sentence: str, span_info: Literal[False]) -> list[str]:
        ...

    @overload
    def extract_keywords(self, sentence: str, span_info: Literal[True]) -> list[tuple[str, int, int]]:
        ...

    @normalize_parameter('sentence')
    def extract_keywords(self, sentence: str, span_info: bool = False) -> Union[list[str], list[tuple[str, int, int]]]:
        output = []
        trie_dict = self.trie_dict

        for idx, char in enumerate(sentence):
            if char in trie_dict:  # do: sentence[idx+1:] because we already check with 'in'? | or just remove this line

                node = trie_dict
                for i, c in enumerate(sentence[idx:]):
                    node = node.get(c)

                    if node is not None:
                        kw = node.get(TrieDict.keyword)
                        if kw:
                            output.append((kw, idx, i)) if span_info else output.append(kw)
                    else:  # no more children
                        break
        return output
