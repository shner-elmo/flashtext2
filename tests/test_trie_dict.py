import unittest

from flashtext2.trie_dict import (
    WordNotFoundError,
    TrieDict,
)


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
            'macronuclear',
            'I love Python',
            'How are you doing?',
            'They say that .NET is great! (just kidding)',
        ]
        self.td = TrieDict()
        for w in self.words:
            self.td.add_keyword(w)

    def test_init(self):
        # TODO add tests for case_sensitive=False
        raise NotImplementedError

    def test_add_word(self):
        td = TrieDict()
        assert td.get_keywords == {}

        for w in self.words:
            td.add_keyword(w)
        assert sorted(td.get_keywords.values()) == sorted(self.words)

        # add same words twice
        for w in self.words:
            td.add_keyword(w)
        assert sorted(td.get_keywords) == sorted(self.words)
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

        # test how it handles two sentences that share the first part
        td = TrieDict()
        td.add_keyword('I love learning Python')
        td.add_keyword('I love riding my skates')
        node = list(td._node_iterator('I love '))[-1]
        self.assertEqual(list(node.keys()), ['learning', 'riding'])

        word = 'I love learning Python'
        self.assertIn(word, container=td)
        td.remove_keyword(word)
        
        self.assertNotIn(word, container=td)
        self.assertEqual(list(node.keys()), ['riding'])
        
        # make sure that removing this word hasn't affected the first word
        word = 'I love riding my skates'
        last_branch_node = list(td._node_iterator(word))[-1]
        self.assertEqual(last_branch_node[td.keyword], word)

        td.remove_keyword(word)
        self.assertEqual(td.trie_dict, {})

    def test_node_iterator(self):
        for node in self.td._node_iterator(self.words[0]):
            assert isinstance(node, dict)
        assert node[self.td.keyword] == self.words[0]  # noqa, last node should contain the keyword

        self.assertRaises(
            WordNotFoundError,
            lambda: list(self.td._node_iterator('non-existent-word'))
        )

    def test_has_word(self):
        self.test_contains_()

    def test_get_keywords(self):
        out = self.td.get_keywords
        assert isinstance(out, dict)
        assert len(out) == len(self.td)

    def test_reset_dict(self):
        self.td.reset_dict()
        assert len(self.td) == 0
        assert self.td.trie_dict == {}

    def test_contains_(self):
        for w in self.words:
            assert w in self.td
            assert w in self.td.get_keywords

            self.td.remove_keyword(w)

            assert w not in self.td
            assert w not in self.td.get_keywords

    def test_iter_(self):
        for word, clean_word in self.td:
            assert word in self.words
            assert word in self.td
            # assert self.td.get_keywords[word] == clean_word
            print(self.td.get_keywords[word])

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
        eval(repr(self.td))

# TODO remove assert statement and use OOP approach instead
