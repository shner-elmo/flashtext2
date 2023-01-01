import unittest

from flashtext2.trie_dict import (
    WordNotFoundError,
    recursive_get_dict_items,
    TrieDict,
)


class TestFunctions(unittest.TestCase):
    def test_recursive_get_dict_items(self):
        pairs = [
            ({}, []),
            ({'a': {}}, [('a', None)]),
            ({'a': {}, 'b': {}, 'c': 3, 'd': None, 'e': []},
             [('a', None), ('b', None), ('c', 3), ('d', None), ('e', [])]),
            ({'a': {'b': {}, 'key': True}}, [('a', None), ('b', None), ('key', True)]),
        ]
        for inp, out in pairs:
            assert list(recursive_get_dict_items(inp)) == out


class TestTrieDict(unittest.TestCase):
    def setUp(self) -> None:
        self.words = [
            'macaco',
            'macaroni',
            'macaroon',
            'machinable',
            'machine',
            'macromolecular',
            'macro',
            'macroscopic',
            'macronuclear'
        ]
        self.td = TrieDict()
        for w in self.words:
            self.td.add_keyword(w)

    def test_add_word(self):
        td = TrieDict()
        assert td.get_keywords() == []

        for w in self.words:
            td.add_keyword(w)
        assert sorted(td.get_keywords()) == sorted(self.words)

        # add same words twice
        for w in self.words:
            td.add_keyword(w)
        assert sorted(td.get_keywords()) == sorted(self.words)
        assert len(td) == len(self.words)

    def test_remove_word(self):
        n = len(self.td)
        for w in self.words:
            assert w in self.td
            self.td.remove_keyword(w)
            assert w not in self.td

            self.assertRaises(
                WordNotFoundError,
                self.td.remove_keyword, w
            )
            n -= 1
        assert n == len(self.td)
        self.assertRaises(
            WordNotFoundError,
            self.td.remove_keyword, 'non-existent-word'
        )

    def test_node_iterator(self):
        for node in self.td.node_iterator(self.words[0]):
            assert isinstance(node, dict)
        assert node[self.td.keyword] == self.words[0]  # noqa, last node should contain the keyword

        self.assertRaises(
            WordNotFoundError,
            lambda: list(self.td.node_iterator('non-existent-word'))
        )

    def test_has_word(self):
        self.test_contains_()

    def test_get_words(self):
        out = self.td.get_keywords()
        assert isinstance(out, list)
        assert isinstance(out[0], str)
        assert len(out) == len(self.td)

        assert len(self.td.get_keywords(5)) == 5

    def test_reset_dict(self):
        self.td.reset_dict()
        assert len(self.td) == 0
        assert self.td.trie_dict == {}

    def test_contains_(self):
        for w in self.words:
            assert self.td.has_word(w)
            assert w in self.td
            assert w in iter(self.td)

            self.td.remove_keyword(w)

            assert not self.td.has_word(w)
            assert w not in self.td
            assert w not in iter(self.td)

    def test_iter_(self):
        for x in self.td:
            assert isinstance(x, str)
            assert x in self.words
            assert x in self.td

        assert list(self.td) == self.words

    def test_len_(self):
        assert len(self.td) == len(self.words)

        n = len(self.td)
        for w in self.words[:3]:
            self.td.remove_keyword(w)
            n -= 1
        assert n == len(self.td)

        self.td.add_keyword('abc')
        self.td.add_keyword('abcdef')
        assert n + 2 == len(self.td)

    def test_eq_(self):
        assert self.td != {}
        assert self.td != 42

        td2 = TrieDict()
        assert self.td != td2

        for w in self.words:
            td2.add_keyword(w)
        assert self.td == td2

    def test_str_(self):
        assert isinstance(str(self.td), str)

    def test_repr_(self):
        assert isinstance(repr(self.td), str)
