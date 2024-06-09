# Better OrderedMultiDict

![License](https://img.shields.io/github/license/JoachimCoenen/Better-OrderedMultiDict)
![GitHub repo size](https://img.shields.io/github/repo-size/JoachimCoenen/Better-OrderedMultiDict?color=0072FF)
[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FJoachimCoenen%2FBetter-OrderedMultiDict&count_bg=%230072FF&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)
[![package version](https://badge.fury.io/py/better_orderedmultidict.svg)](https://pypi.python.org/pypi/better_orderedmultidict)
[![supported python versions](https://img.shields.io/pypi/pyversions/better_orderedmultidict.svg)](https://pypi.python.org/pypi/better_orderedmultidict)
  <!-- <a href="https://pypi.python.org/pypi/better_orderedmultidict"><img src="https://badge.fury.io/py/better_orderedmultidict.svg"></a> -->
  <!-- <img src="https://img.shields.io/pypi/l/better_orderedmultidict.svg"> -->
  <!--<a href="https://pypi.python.org/pypi/better_orderedmultidict"><img src="https://img.shields.io/pypi/pyversions/better_orderedmultidict.svg"></a>-->

<!-- TOC -->
  * [Overview](#overview)
  * [Differences to omdict](#differences-to-omdict)
  * [Performance Comparison](#performance-comparison)
  * [Examples](#examples)
  * [Installation](#installation)
<!-- TOC -->

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
    print(list(omdict(items).values()))           # prints [111]
    print(list(OrderedMultiDict(items).values())) # prints [1, 11, 111]
    ```
  * `OrderedMultiDict` is faster:  
    * Initialization from a list is up to **2.5x faster**.  
    * Iterating over _all_ values is between **3.8x and 6.9x faster**. 
    * For a more detailed performance comparison see the [Performance Comparison](#performance-comparison) section.
  * But `OrderedMultiDict` does not retain full method parity with `dict`, so it can not be used as a drop-in replacement.



## Performance Comparison
Creating / iterating over dictionary with 500'000 entries with all keys being different:

|                          | Better <br/>OrderedMultiDict |    omdict | OrderedDict |
|--------------------------|-----------------------------:|----------:|------------:|
| create                   |                    527.74 ms | 579.80 ms |    82.10 ms |
| iterate over items       |                     20.19 ms |  95.60 ms |    39.49 ms |
| iterate over values      |                     20.37 ms |  77.96 ms |    31.64 ms |
| iterate over keys        |                     20.32 ms |  77.27 ms |    22.18 ms |
| iterate over unique keys |                     53.24 ms |  35.41 ms |    21.77 ms |


Creating / iterating over dictionary with 500'000 entries, but only 100 unique keys distributed randomly:

|                          | Better <br/>OrderedMultiDict |    omdict |  OrderedDict |
|--------------------------|-----------------------------:|----------:|-------------:|
| create                   |                    198.91 ms | 488.07 ms | ~~37.40 ms~~ |
| iterate over items       |                     19.08 ms |  93.48 ms |  ~~0.01 ms~~ |
| iterate over values      |                     18.52 ms | 124.64 ms |  ~~0.00 ms~~ |
| iterate over keys        |                      9.51 ms |  65.44 ms |  ~~0.00 ms~~ |
| iterate over unique keys |                     15.02 ms |   0.01 ms |    < 0.01 ms |

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

### Iterating over all keys

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