## Next Version
### Fixes
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
