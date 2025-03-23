# Better OrderedMultiDict

![License](https://img.shields.io/github/license/JoachimCoenen/Better-OrderedMultiDict)
![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FJoachimCoenen%2FBetter-OrderedMultiDict&count_bg=%230072FF&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)
[![PyPI version](https://badge.fury.io/py/better-orderedmultidict.svg)](https://badge.fury.io/py/better-orderedmultidict)
[![PyPI - Python Versions](https://img.shields.io/pypi/pyversions/Better-OrderedMultiDict?color=0072FF)](https://pypi.python.org/pypi/better_orderedmultidict)
  <!-- <a href="https://pypi.python.org/pypi/better_orderedmultidict"><img src="https://badge.fury.io/py/better_orderedmultidict.svg"></a> -->
  <!-- <img src="https://img.shields.io/pypi/l/better_orderedmultidict.svg"> -->
  <!--<a href="https://pypi.python.org/pypi/better_orderedmultidict"><img src="https://img.shields.io/pypi/pyversions/better_orderedmultidict.svg"></a>-->


## Overview

Better OrderedMultiDict provides two fast ordered multivalued dictionaries: `OrderedMultiDict` and `DeOrderedMultiDict`.

Multivalued means that there can be multiple items with the same key:  
```python
from better_orderedmultidict import OrderedMultiDict
dictionary = OrderedMultiDict()
dictionary.add("Schrödinger's cat", "dead")
dictionary.add("Schrödinger's cat", "alive")
print(dictionary.getall("Schrödinger's cat"))  #["dead", "alive"]
```

Ordered means that the insertion order of all keys and values is retained:
```python
from better_orderedmultidict import OrderedMultiDict
dictionary = OrderedMultiDict()
dictionary.add("Schrödinger's cat", "alive")
dictionary.add("Pavlov's dog", "conditioned")
dictionary.add("Schrödinger's cat", "dead")

print(list(dictionary.values()))      # ["alive", "conditioned", "dead"]
print(list(dictionary.unique_keys())) # ["Schrödinger's cat", "Pavlov's dog"]
print(list(dictionary.keys()))        # ["Schrödinger's cat", "Pavlov's dog", "Schrödinger's cat"]

dictionary.poplastitem()

print(list(dictionary.values()))      # ["alive", "conditioned"]
print(list(dictionary.unique_keys())) # ["Schrödinger's cat", "Pavlov's dog"]
print(list(dictionary.keys()))        # ["Schrödinger's cat", "Pavlov's dog"]
```

Better OrderedMultiDict requires Python 3.12+ and is fully type annotated.




## Performance Comparison
Creating / iterating over dictionary with 500'000 entries with all keys being different:

|                                 | OrderedMultiDict | [omdict][omdict_LINK] |       speedup | | [boltons][boltons_LINK] </br>OrderedMultiDict |       speedup |
|---------------------------------|-----------------:|----------------------:|--------------:|-|----------------------------------------------:|--------------:|
| create                          |         117.6 ms |              285.8 ms |          2.4x | |                                      136.2 ms |          1.2x |
| addall / addlist                |          67.4 ms |              158.2 ms |          2.3x | |                                       66.6 ms | <i>slower</i> |
| update / updateall<sup>1)</sup> |         133.1 ms |              281.3 ms |          2.1x | |                                      175.1 ms |          1.3x |
| extend / update_extend          |          92.6 ms |                    -- |            -- | |                                      145.9 ms |          1.6x |
| copy                            |          52.3 ms |              335.7 ms |          6.4x | |                                      195.7 ms |          3.7x |
| iterate over items              |           2.2 ms |               45.2 ms |         20.3x | |                                       46.2 ms |         20.8x |
| iterate over values             |           5.7 ms |               33.5 ms |          5.8x | |                                       33.1 ms |          5.8x |
| iterate over keys               |           5.8 ms |               33.3 ms |          5.8x | |                                       15.8 ms |          2.7x |
| iterate over unique keys        |          16.5 ms |                5.8 ms | <i>slower</i> | |                                       32.0 ms |          1.9x |
| pop last item until empty       |         138.0 ms |              242.6 ms |          1.8x | |                                      403.4 ms |          2.9x |


Creating / iterating over dictionary with 500'000 entries, but only 100 unique keys distributed randomly:

|                                 | OrderedMultiDict | [omdict][omdict_LINK] |       speedup | | [boltons][boltons_LINK] </br>OrderedMultiDict | speedup |
|---------------------------------|-----------------:|----------------------:|--------------:|-|----------------------------------------------:|--------:|
| create                          |          46.7 ms |              249.2 ms |          5.3x | |                                      120.9 ms |    2.6x |
| addall / addlist                |          59.6 ms |              156.9 ms |          2.6x | |                                       67.3 ms |    1.1x |
| update / updateall<sup>1)</sup> |          53.0 ms |              250.5 ms |          4.7x | |                                      116.0 ms |    2.2x |
| extend / update_extend          |          51.0 ms |                    -- |            -- | |                                      117.5 ms |    2.3x |
| copy                            |           9.1 ms |              281.6 ms |         30.8x | |                                      133.9 ms |   14.6x |
| iterate over items              |           2.5 ms |               44.0 ms |         17.7x | |                                       29.7 ms |   11.9x |
| iterate over values             |           7.3 ms |               31.3 ms |          4.3x | |                                       31.3 ms |    4.3x |
| iterate over keys               |          11.9 ms |               31.0 ms |          2.6x | |                                       18.1 ms |    1.5x |
| iterate over unique keys        |          18.2 ms |           &lt; 0.1 ms | <i>slower</i> | |                                       19.0 ms |    1.0x |
| pop last item until empty       |         110.0 ms |              215.1 ms |          2.0x | |                                      163.3 ms |    1.5x |


1):  `omdict. updateall()` has slightly different behavior: `omdict` keeps the positions for already existing keys, but `OrderedMultiDict` and bolton's `OrderedMultiDict` do not:

```python
from better_orderedmultidict import OrderedMultiDict
from orderedmultidict import omdict

initial = [(1, 1), (2, 2), (1, 11), (2, 22), (3, 3)]
omd1 = OrderedMultiDict(initial)
omd2 = omdict(initial)
updates = [(1, '1'), (1, '11')]
omd1.update(updates)
omd2.updateall(updates)
print(list(omd1.items()))         # [(2, 2), (2, 22), (3, '3'), (1, '1'), (1, '11')]
print(list(omd2.iterallitems()))  # [(1, '1'), (2, 2), (1, '11'), (2, 22), (3, '3')]
```

## Differences between `OrderedMultiDict` and `DeOrderedMultiDict`:

Both provide the same API, but have slightly different performance characteristics:

- `OrderedMultiDict` is generally about 1.5x - 4x faster and uses a lot *less* memory per *unique* key. But method `.popfirstitem()` has linear performance characteristics O(n)
- `DeOrderedMultiDict` is generally slower and uses a lot *more* memory per *unique* key. But method `.popfirstitem()` has constant performance characteristics O(1)


Creating / iterating over dictionary with 500000 entries with all keys being different:

|                                 | OrderedMultiDict |  DeOrderedMultiDict |    OrderedMultiDict <br>is faster: |
|---------------------------------|-----------------:|--------------------:|-----------------------------------:|
| create                          |         101.8 ms |            161.4 ms |                               1.6x |
| copy                            |          51.9 ms |            146.8 ms |                               2.8x |
| iterate over items              |           2.2 ms |             10.3 ms |                               4.6x |
| iterate over unique keys        |          15.4 ms |             23.4 ms |                               1.5x |
| pop first item until empty      |   **38.7 s (!)** |            194.9 ms |            &gt;190x  <i>slower</i> |
| pop last item until empty       |         143.2 ms |            180.3 ms |                               1.3x |

## Examples

### OrderedMultiDict can have multiple values per key:

```python
from better_orderedmultidict import OrderedMultiDict
omd = OrderedMultiDict()
omd[1] = 1
print(omd[1])   # prints: 1

omd.add(1, 11)
print(omd[1])           # prints: 11
print(omd.get(1))       # prints: 11
print(omd.getlast(1))   # prints: 11
print(omd.getfirst(1))  # prints: 1
print(omd.getall(1))    # prints: [1, 11]

# adding multiple values at once:
omd.addall(2, [2, 22])
print(omd.getall(2))    # prints: [2, 22]

# __setitem__ overrides all existing entries for the given key:
omd[1] = 111
print(list(omd.values()))  # prints: [2, 22, 111]
```

### OrderedMultiDict retains insertion order:

```python
from better_orderedmultidict import OrderedMultiDict
omd = OrderedMultiDict()
omd.addall(1, [1, 11])
omd.add(2, 2)
omd.add(3, 3)
omd.add(2, 22)
omd.add(3, 33)
omd.add(1, 111)

print(omd.getall(1))    # prints: [1, 11, 111]
print(list(omd.values()))  # prints: [1, 11, 2, 3, 22, 33, 111]

del omd[2]
print(list(omd.values()))  # prints: [1, 11, 3, 33, 111]
omd.popfirst(3)
print(list(omd.values()))  # prints: [1, 11, 33, 111]
omd.poplast(1)
print(list(omd.values()))  # prints: [1, 11, 33]
omd.poplast(1)
print(list(omd.values()))  # prints: [1, 33]
```

### Method parity with dict is only somewhat retained

```python
from better_orderedmultidict import OrderedMultiDict
d, omd = dict(), OrderedMultiDict()
d.update([(1,1), (1,11), (2,2), (2,22)])
omd.update([(1,1), (1,11), (2,2), (2,22)])

print(d[1], omd[1])  # prints: (11, 11)
d[3] = omd[3] = 3
print(d[3], omd[3])  # prints: (3, 3)

d[3] = omd[3] = 33
print(d[3], omd[3])  # prints: (33, 33)

# But there are differences:
print(len(d), len(omd))  # prints: (3, 5)
d.pop(2)
omd.pop(2)
print(d.get(2), omd.get(2))  # prints: (None, 2)
```

### Iterating over unique keys

```python
from better_orderedmultidict import OrderedMultiDict
omd = OrderedMultiDict([(1,1), (2,2), (1,11), (2,22)])

print(len(omd.keys()))  # prints: 4
print(len(omd.unique_keys()))  # prints: 2

for key in reversed(omd.unique_keys()):
    print(f"{key}: {omd.getall(key)}")
# prints:
# 1: [1, 11]
# 2: [2, 22]
```


## Installation

Installation is simple:

```
$ pip install better_orderedmultidict
```


## Changelog
[CHANGES.md](./CHANGES.md)


[omdict_LINK]:  https://github.com/gruns/orderedmultidict  "omdict git repository"
[boltons_LINK]: https://github.com/mahmoud/boltons  "boltons git repository"
