## 0.2.2
### Fixes
 * Fixed a bug where when creating, updating, or extending an OrderedMultiDict using a collection of lists instead of tuples and then changing one of the lists causes the OrderedMultiDict to break in very subtle ways.
    ```pycon
    >>> from better_orderedmultidict import OrderedMultiDict
    ... items = [['0', 'zero'], ['1', 'one']]
    ... dictionary = OrderedMultiDict(items)
    >>> items[0][:] = ['2', 'two']  # change one item 'tuple'
    >>> '2' in dictionary  # is False, as expected
    False
    >>> '2' in set(dictionary.keys())  # should also be False
    True
    ```
 * Fixed a bug where when creating, updating, or extending an OrderedMultiDict could leave it in a broken state, if some of the keys are not hashable.
 * Fixed mypy issues


## 0.2.1
 * Fixed README.md


## 0.2.0
### Non-Breaking Changes & Improvements
 * Overall performance improvements (up to 2x)
 * Added `DeOrderedMultiDict` (double-ended OrderedMultiDict) which has better performance characteristics for `.popfirst(key)` and `popfirstitem()`
 * Extended performance tests


## 0.1.0
### Breaking Changes
 * Renamed `.update()` to `.extend()`
 * Added new `.update()` with different behavior

### Non-Breaking Changes & Improvements
 * Improved performance of `.addall()`
 * Extended performance tests
