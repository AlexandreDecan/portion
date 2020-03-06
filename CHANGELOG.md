# Changelog

## 2.0.0 (2020-03-06)

### Added
 - `i.empty` to check for interval emptiness.
 - `i.atomic` to check for interval atomicity.
 - An `adjacent` method to test whether two intervals are adjacent.
 - `i.__getitem__` supports slices.
 - Infinities define a hash value.
 - Static method `Interval.from_atomic(left, lower, upper, right)` to create an interval composed of a single atomic interval (replaces `AtomicInterval(left, lower, upper, right)`).

### Changed
 - (breaking) `python-intervals` has been renamed `portion`.
 - (breaking) Many (optional) parameters are converted to keyword-only arguments:
   * for `from_string` and `to_string`: `bound`, `disj`, `sep`, `left_open`, `left_closed`, `right_open`, `right_closed`, `pinf` and `ninf`;
   * for `from_data` and `to_data`: `pinf` and `ninf`;
   * for `iterate`: `base` and `reverse`;
   * for `Interval.replace`: `ignore_inf`.
 - (breaking) `incr` is replaced by `step` in `iterate`.
 - (breaking) For consistency with `range`, the `step` parameter in `iterate` is always added even if `reverse=True`.
 - (breaking) `i.enclosure` is a property and no longer a method.
 - (breaking) Indexing or iterating on the atomic intervals of an `Interval` returns `Interval` instances instead of `AtomicInterval` ones.
 - (breaking) An interval is hashable if and only if its bounds are hashable.
 - Huge performance increase for creation, union, intersection, complement and difference of intervals ([#21](https://github.com/AlexandreDecan/portion/issues/21)).
 - `CLOSED` and `OPEN` are members of the `Bound` enumeration.
 - Large refactoring to encapsulate `AtomicInterval` and all its operations in `Interval`.
 - Restructure package in modules instead of a flat file.
 - Reorganise tests in modules and classes instead of a flat file.
 - Reorganise changelog with explicit categories.

### Removed
 - (breaking) Drop support for Python 2.7 and 3.4 since they reached end-of-life.
 - (breaking) `AtomicInterval` is a `namedtuple` and is no longer part of the public APP.
 - (breaking) Remove `i.to_atomic()` (use `i.enclosure` instead).
 - (breaking) Remove `i.is_empty()` (use `i.empty` instead).
 - (breaking) Remove `i.is_atomic()` (use `i.atomic` instead).
 - (breaking) `CLOSED` and `OPEN` do no longer define an implicit Boolean value. Use `~` instead of `not` to invert a bound.
 - (breaking) Remove deprecated `permissive` in `i.overlaps`.
 - (breaking) Remove `adjacent` in `i.overlaps`, use `i.adjacent` method instead.
 - Package meta-data (e.g., `__version__`, `__url__`, etc.) moved to `setup.py`.

### Fixed
 - Fix an issue where an interval can be composed of duplicated empty intervals ([#19](https://github.com/AlexandreDecan/portion/issues/19)).



## 1.10.0 (2019-09-26)

### Added
 - `IntervalDict` has a `.combine` method to merge its keys and values with another `IntervalDict`.


## 1.9.0 (2019-09-13)

### Added
 - Discrete iteration on the values of an interval with `iterate`.
 - Map intervals to data with the dict-like `IntervalDict` structure.

### Changed
 - Faster comparisons between arbitrary values and intervals.
 - Deprecate `permissive` in `.overlaps` in favour of `adjacent`.

### Fixed
 - `.union` when intervals share a bound, one inclusive and one exclusive ([#12](https://github.com/AlexandreDecan/portion/issues/12)).
 - `.overlaps` when intervals share a lower bound, and one interval is contained within the other one ([#13](https://github.com/AlexandreDecan/portion/issues/13)).


## 1.8.0 (2018-12-15)

### Added
 - Intervals have a `.left`, `.lower`, `.upper`, and `.right` attribute that refer to its enclosure.
 - Intervals have a `.replace` method to create new intervals based on the current one. This method accepts both values and functions.
 - Intervals have an `.apply` method to apply a function on the underlying atomic intervals.
 - Intervals can be compared with single values as well.

### Changed
 - `P.empty()` returns the same instance to save memory.
 - Infinities are singleton objects.
 - Set `len(P.empty()) = 1` and `P.empty()[0] == P.empty().to_atomic()` for consistency.


## 1.7.0 (2018-12-06)

### Added
 - Import from and export to Python built-in data types (a list of 4-uples) with `from_data` and `to_data` ([#6](https://github.com/AlexandreDecan/portion/issues/6)).
 - Examples for arbitrary interval transformations.


## 1.6.0 (2018-08-29)

### Added
 - Support for customized infinity representation in `to_string` and `from_string` ([#3](https://github.com/AlexandreDecan/portion/issues/3)).


## 1.5.4 (2018-07-29)

### Fixed
 - `.overlaps` ([#2](https://github.com/AlexandreDecan/portion/issues/2)).


## 1.5.3 (2018-06-21)

### Fixed
 - Invalid `repr` for atomic singleton intervals.


## 1.5.2 (2018-06-15)

### Fixed
 - Invalid comparisons when both `Interval` and `AtomicInterval` are compared.


## 1.5.1 (2018-04-25)

### Fixed
 - [#1](https://github.com/AlexandreDecan/portion/issues/1) by making empty intervals always resolving to `(P.inf, -P.inf)`.


## 1.5.0 (2018-04-17)

### Added
 - `Interval.__init__` accepts `Interval` instances in addition to `AtomicInterval` ones.


## 1.4.0 (2018-04-17)

### Added
 - Function `P.to_string` to export an interval to a string, with many options to customize the representation.
 - Function `P.from_string` to create an interval from a string, with many options to customize the parsing.


## 1.3.2 (2018-04-13)

### Added
 - Support for Python 2.7.


## 1.3.1 (2018-04-12)

### Fixed
 - More tests to cover all comparisons.
 - Define `__slots__` to lower memory usage, and to speed up attribute access.
 - Define `Interval.__rand__` (and other magic methods) to support `Interval` from `AtomicInterval` instead of
 having a dedicated piece of code in `AtomicInterval`.
 - `__all__` properly defined.


## 1.3.0 (2018-04-04)

### Added
 - Meaningful `<=` and `>=` comparisons for intervals.


## 1.2.0 (2018-04-04)

### Added
 - `Interval` supports indexing to retrieve the underlying `AtomicInterval` objects.


## 1.1.0 (2018-04-04)

### Added
 - Both `AtomicInterval` and `Interval` are fully comparable.
 - `singleton(x)` to create a singleton interval [x].
 - `empty()` to create an empty interval.
 - `Interval.enclosure()` that returns the smallest interval that includes the current one.

### Changed
 - Interval simplification is in O(n) instead of O(n*m).
 - `AtomicInterval` objects in an `Interval` are sorted by lower and upper bounds.


## 1.0.4 (2018-04-03)

### Fixed
 - All operations of `AtomicInterval` (except overlaps) accept `Interval`.
 - Raise `TypeError` instead of `ValueError` if type is not supported (coherent with `NotImplemented`).


## 1.0.3 (2018-04-03)

 - Initial release on PyPP.


## 1.0.0 (2018-04-03)

 - Initial release.
