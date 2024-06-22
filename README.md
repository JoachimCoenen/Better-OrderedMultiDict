# Better OrderedMultiDict

![License](https://img.shields.io/github/license/JoachimCoenen/Better-OrderedMultiDict)
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

Better OrderedMultiDict provides `OrderedMultiDict`, a fast[*](#performance-comparison), ordered multivalued dictionary.

`OrderedMultiDict` is multivalued, which means that there can be multiple items with the same key:  
```python
from better_orderedmultidict import OrderedMultiDict
dictionary = OrderedMultiDict()
dictionary.add("umfahren", "to drive around")
dictionary.add("umfahren", "to drive over, to knock sth. over")
print(dictionary.getall("umfahren"))  # ["to drive around", "to drive over, to knock sth. over"]
```

`OrderedMultiDict` retains the insertion order of all keys and values:
```python
from better_orderedmultidict import OrderedMultiDict
dictionary = OrderedMultiDict()
dictionary.add('a', 'A1')
dictionary.add('b', 'B')
dictionary.add('a', 'A2')
print(', '.join(dictionary.values()))      # A1, B, A2
print(', '.join(dictionary.unique_keys())) # a, b

dictionary.popfirstitem()
print(', '.join(dictionary.values()))      # B, A2
print(', '.join(dictionary.unique_keys())) # b, a
```

Better OrderedMultiDict requires Python 3.12+ and is fully type annotated.




## Performance Comparison
Creating / iterating over dictionary with 500'000 entries with all keys being different:

|                                 | OrderedMultiDict | [omdict][omdict_LINK] |       speedup | | [bolton][bolton_LINK] </br>OrderedMultiDict | speedup |
|---------------------------------|-----------------:|----------------------:|--------------:|-|--------------------------------------------:|--------:|
| create                          |         164.3 ms |              548.0 ms |          3.2x | |                                    304.1 ms |    1.9x |
| addall / addlist                |          82.3 ms |              311.7 ms |          3.8x | |                                    139.6 ms |    1.7x |
| update / updateall<sup>1)</sup> |         262.2 ms |              531.5 ms |          2.0x | |                                    325.5 ms |    1.2x |
| extend / update_extend          |         156.4 ms |                    -- |            -- | |                                    285.5 ms |    1.8x |
| copy                            |         100.1 ms |              646.7 ms |          6.5x | |                                    350.7 ms |    3.4x |
| iterate over items              |          11.2 ms |               97.0 ms |          8.6x | |                                     81.0 ms |    7.2x |
| iterate over values             |          12.3 ms |               77.3 ms |          6.3x | |                                     81.3 ms |    6.3x |
| iterate over keys               |          12.6 ms |               78.6 ms |          6.2x | |                                     53.0 ms |    4.2x |
| iterate over unique keys        |          42.4 ms |               23.7 ms | <i>slower</i> | |                                     94.1 ms |    2.2x |
| pop last item until empty       |         268.7 ms |              501.3 ms |          1.9x | |                                    884.3 ms |    3.2x |


Creating / iterating over dictionary with 500'000 entries, but only 100 unique keys distributed randomly:

|                                 | OrderedMultiDict | [omdict][omdict_LINK] |       speedup | | [bolton][bolton_LINK] </br>OrderedMultiDict | speedup |
|---------------------------------|-----------------:|----------------------:|--------------:|-|--------------------------------------------:|--------:|
| create                          |          89.7 ms |              484.5 ms |          5.4x | |                                    258.8 ms |    2.7x |
| addall / addlist                |          84.7 ms |              317.1 ms |          3.7x | |                                    137.5 ms |    1.6x |
| update / updateall<sup>1)</sup> |         110.8 ms |              491.8 ms |          4.4x | |                                    278.2 ms |    2.5x |
| extend / update_extend          |          91.3 ms |                    -- |            -- | |                                    257.3 ms |    2.7x |
| copy                            |          24.0 ms |              595.8 ms |         24.8x | |                                    307.8 ms |   12.4x |
| iterate over items              |          11.2 ms |              102.5 ms |          9.2x | |                                     77.4 ms |    6.8x |
| iterate over values             |          17.0 ms |               81.0 ms |          4.8x | |                                     80.1 ms |    4.8x |
| iterate over keys               |          16.9 ms |               78.3 ms |          4.6x | |                                     50.5 ms |    3.0x |
| iterate over unique keys        |          18.8 ms |           &lt; 0.1 ms | <i>slower</i> | |                                     36.0 ms |    1.9x |
| pop last item until empty       |         235.7 ms |              484.8 ms |          2.1x | |                                    401.8 ms |    1.7x |


1):  `omdict. updateall()` has slightly different behavior: `omdict` keeps the positions for already existing keys, but `OrderedMultiDict` and bolton's `OrderedMultiDict` do not:
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
