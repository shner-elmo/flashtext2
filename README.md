# Trie Dict

----

Import and initialize the Trie Dict:
```py
from flashtext2.trie_dict import TrieDict
td = TrieDict()
```

Add a bunch of words:
```py
words = ['machinable', 'machine', 'macromolecular', 'macro']
for w in words:
    td.add_word(w)
```

Check if it contains a given word:
```py
td.has_word('mac'), td.has_word('macro')
```
```
(False, True)
```

Amount of words stored in the Trie Dict
```py
len(td)
```
```
4
```

We can check out the tree by with the following attribute:
```py
td.trie_dict
```
```
{'m': {'a': {'c': {'h': {'i': {'n': {'a': {'b': {'l': {'e': {'__keyword__': 'machinable'}}}},
       'e': {'__keyword__': 'machine'}}}},
    'r': {'o': {'m': {'o': {'l': {'e': {'c': {'u': {'l': {'a': {'r': {'__keyword__': 'macromolecular'}}}}}}}}},
      '__keyword__': 'macro'}}}}}}
```

To get all the word from the tree:
```py
td.get_words()
```
```
['machinable', 'machine', 'macromolecular', 'macro']
```
