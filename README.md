# Better OrderedMultiDict

![License](https://img.shields.io/github/license/JoachimCoenen/Better-OrderedMultiDict)
![GitHub repo size](https://img.shields.io/github/repo-size/JoachimCoenen/Better-OrderedMultiDict?color=0072FF)
![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FJoachimCoenen%2FBetter-OrderedMultiDict&count_bg=%230072FF&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)
[![PyPI version](https://badge.fury.io/py/better-orderedmultidict.svg)](https://badge.fury.io/py/better-orderedmultidict)
[![PyPI - Python Versions](https://img.shields.io/pypi/pyversions/Better-OrderedMultiDict?color=0072FF)](https://pypi.python.org/pypi/better_orderedmultidict)
  <!-- <a href="https://pypi.python.org/pypi/better_orderedmultidict"><img src="https://badge.fury.io/py/better_orderedmultidict.svg"></a> -->
  <!-- <img src="https://img.shields.io/pypi/l/better_orderedmultidict.svg"> -->
  <!--<a href="https://pypi.python.org/pypi/better_orderedmultidict"><img src="https://img.shields.io/pypi/pyversions/better_orderedmultidict.svg"></a>-->

<!-- TOC 
  * [Overview](#overview)
  * [Differences to omdict](#differences-to-omdict)
  * [Performance Comparison](#performance-comparison)
  * [Examples](#examples)
  * [Installation](#installation)
 TOC -->

## Overview

Better OrderedMultiDict provides `OrderedMultiDict`, a fast[*](#performance-comparison), ordered multivalued dictionary implementation.

`OrderedMultiDict` is multivalued, which means that there can be multiple items with the same key:  
```python
from better_orderedmultidict import OrderedMultiDict
dictionary = OrderedMultiDict()
dictionary.add("umfahren", "to drive around")
dictionary.add("umfahren", "to drive over, to knock sth. down")
print(dictionary.getall("umfahren"))  # ["to drive around", "to drive over, to knock sth. down"]
```

`OrderedMultiDict` retains the insertion order of all keys and values:
```python
from better_orderedmultidict import OrderedMultiDict
dictionary = OrderedMultiDict()
dictionary.add('a', 'A1')
dictionary.add('b', 'B')
dictionary.add('a', 'A2')
print(', '.join(dictionary.values()))    # A1, B, A2
print(', '.join(dictionary.getall('a'))) # A1, A2
```

Better OrderedMultiDict requires Python 3.12+ and is fully type annotated.

## Differences to [omdict](https://github.com/gruns/orderedmultidict):
  * `OrderedMultiDict` tries to provide a nicer API with less surprising behavior. For example:  
    ```python
    from better_orderedmultidict import OrderedMultiDict
    from orderedmultidict import omdict
    items = [(1, 1), (1, 11), (1, 111)]
    print(list(omdict(items).values()))           # prints [111] (where have the other two values gone?)
    print(list(OrderedMultiDict(items).values())) # prints [1, 11, 111]
    ```
  * `OrderedMultiDict` is faster:  
    * Initialization from a list is up to **2.5x faster**.  
    * Iterating over _all_ values is about **4x faster**. 
    * For a more detailed performance comparison see the [Performance Comparison](#performance-comparison) section.
  * But `OrderedMultiDict` does not retain full method parity with `dict`, so it can not be used as a drop-in replacement.



## Performance Comparison
Creating / iterating over dictionary with 500'000 entries with all keys being different:

|                                 | OrderedMultiDict |    omdict |       speedup |
|---------------------------------|-----------------:|----------:|--------------:|
| create                          |        496.44 ms | 554.75 ms |          1.1x |
| addall / addlist                |         88.55 ms | 321.76 ms |          3.6x |
| update / updateall<sup>1)</sup> |        400.18 ms | 546.76 ms |          1.4x |
| copy                            |        301.60 ms | 655.58 ms |          2.2x |
| iterate over items              |         18.51 ms |  91.58 ms |          4.9x |
| iterate over values             |         18.51 ms |  74.17 ms |          4.0x |
| iterate over keys               |         17.83 ms |  73.77 ms |          4.1x |
| iterate over unique keys        |         47.33 ms |  33.68 ms | <i>slower</i> |


Creating / iterating over dictionary with 500'000 entries, but only 100 unique keys distributed randomly:

|                                 | OrderedMultiDict |     omdict |       speedup |
|---------------------------------|-----------------:|-----------:|--------------:|
| create                          |        188.45 ms |  468.74 ms |          2.5x |
| addall / addlist                |        103.47 ms |  305.90 ms |          3.0x |
| update / updateall<sup>1)</sup> |        100.85 ms | 1465.81 ms |         14.5x |
| copy                            |         47.14 ms |  568.60 ms |         12.1x |
| iterate over items              |         18.18 ms |   90.75 ms |          5.0x |
| iterate over values             |         18.41 ms |   72.72 ms |          4.0x |
| iterate over keys               |          9.06 ms |   62.71 ms |          6.9x |
| iterate over unique keys        |         14.74 ms |    0.01 ms | <i>slower</i> |


1):  `omdict. updateall()` and `OrderedMultiDict.update()` have slightly different behavior for where `omdict` keeps the positions for already existing keys, but `OrderedMultiDict` does not:
```python
from better_orderedmultidict import OrderedMultiDict
from orderedmultidict import omdict
omd1 = OrderedMultiDict([(1,1), (2,2), (1,11), (2, 22), (3,3)])
omd2 = omdict([(1,1), (2,2), (1,11), (2, 22), (3,3)])
omd1.update([(1, '1'), (3, '3'), (1, '11')])
omd2.updateall([(1, '1'), (3, '3'), (1, '11')])
print(list(omd1.items()))         # prints [(2, 2), (2, 22), (1, '1'), (3, '3'), (1, '11')]
print(list(omd2.iterallitems()))  # prints [(1, '1'), (2, 2), (1, '11'), (2, 22), (3, '3')]
```

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
