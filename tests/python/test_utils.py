import unittest

from flashtext2.utils import yield_nested_dict_items


class TestUtils(unittest.TestCase):
    def test_yield_nested_dict_items(self):
        pairs = [
            ({}, []),
            ({'a': {}}, [('a', None)]),
            ({'a': {}, 'b': {}, 'c': 3, 'd': None, 'e': []},
             [('a', None), ('b', None), ('c', 3), ('d', None), ('e', [])]),
            ({'a': {'b': {}, 'key': True}}, [('a', None), ('b', None), ('key', True)]),
        ]
        for inp, out in pairs:
            assert list(yield_nested_dict_items(inp)) == out


