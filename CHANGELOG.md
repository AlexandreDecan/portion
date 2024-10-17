# Changelog

## 2.6.0 (2024-10-17)

### Added
 - The `how` function of `combine` can access the current interval if `pass_interval` is set (see [#97](https://github.com/AlexandreDecan/portion/issues/97)).



## 2.5.0 (2024-09-18)

### Added
 - The `combine` method of an `IntervalDict` accepts a `missing` parameter to fill values for non-overlapping keys (see [#96](https://github.com/AlexandreDecan/portion/issues/96)).
 - A recipe to `combine` more than two `IntervalDict` (see [#95](https://github.com/AlexandreDecan/portion/issues/95#issuecomment-2351435891)).

### Changed
 - Drop official support for Python 3.7.



## 2.4.2 (2023-12-06)

### Fixed
 - Import error when using `create_api` in Python 3.10+ (see [#87](https://github.com/AlexandreDecan/portion/issues/87)).



## 2.4.1 (2023-07-19)

### Fixed
 - Import error when using `create_api` outside a REPL (see [#85](https://github.com/AlexandreDecan/portion/issues/85)).



## 2.4.0 (2023-03-13)

### Added
 - An `AbstractDiscreteInterval` class to ease the creation of specialized discrete intervals (experimental).
 - A `create_api` function to generate an API similar to the one of `portion` but configured to use a given subclass of `Interval` (experimental, see [Specialize & customize intervals](https://github.com/AlexandreDecan/portion#specialize--customize-intervals)).

### Changed
 - Speed up `repr` and `to_string` for `Interval` instances (see [#76](https://github.com/AlexandreDecan/portion/issues/76), adm271828).
 - Some internal changes to ease subclassing:
   * `from_string` and `from_data` accepts a `klass` parameter to specify which class should be used to create `Interval` instances (default is `Interval`).
   * Add a `klass` parameter for `open`, `closed`, `openclosed`, `closedopen`, `singleton` and `empty` (default is `Interval`).
   * Add a `_klass` class attribute in `IntervalDict` to specify how to create `Interval` instances (default is `Interval`).
   * `IntervalDict` uses `self.__class__` to preserve subclasses when creating new instances.



## 2.3.1 (2023-01-28)

### Changed
 - Speed up lookups in `IntervalDict` for non-interval keys.
 - Speed up `iterate` by no longer creating singleton instances under the hood.
 - Drop official support for Python 3.6.

### Fixed
 - Infinite recursion when a subclass of an `Interval` is compared using `>` with an `Interval` instance (see [#75](https://github.com/AlexandreDecan/portion/issues/75)).



## 2.3.0 (2022-08-31)

### Added
 - Support for Python 3.10.
 - `IntervalDict.as_dict` has an optional `atomic=False` parameter that, if set to `True`, returns intervals that are atomic.
 - Experimental support for structural pattern matching (on `left`, `lower`, `upper` and `right`).

### Fixed
 - (breaking) Set `list(P.empty()) == []`, i.e., the empty interval is a disjunction of no interval (see [#72](https://github.com/AlexandreDecan/portion/issues/72)).
 - (breaking) For consistency, the empty interval is never `<`, `>`, `<=`, nor `>=` when compared to another interval.
 - Comparing an interval and a value is deprecated since it is ill-defined when the value is on the left of `<=` or `>=`. Convert values to singletons first.



## 2.2.0 (2021-09-14)

### Added
 - Support [PEP 517](https://www.python.org/dev/peps/pep-0517).

### Changed
 - Some internal changes to ease subclassing `Interval`(see [#58](https://github.com/AlexandreDecan/portion/issues/58)):
   * Use `self.__class__` instead of `Interval` to create new instances;
   * Deprecate and move `mergeable` function to `Interval._mergeable` class method;
   * `Interval.from_atomic` is now a class method instead of a static method.
 - Speed up lookups in `IntervalDict` ([#65](https://github.com/AlexandreDecan/portion/issues/65), Jeff Trull).
 - Speed up removals in `IntervalDict`.
 - Speed up intersection for non-overlapping intervals ([#66](https://github.com/AlexandreDecan/portion/issues/66), Jeff Trull).
 - Speed up `.overlaps` and `.contains` for non-overlapping intervals/items.



## 2.1.6 (2021-04-17)

### Changed
 - Drop official support for Python 3.5.
 - Use `black` as official code formatting.

### Fixed
 - `from_string`raises a `ValueError` if given string cannot be parsed to an interval ([#57](https://github.com/AlexandreDecan/portion/issues/57)).



## 2.1.5 (2021-02-28)

### Fixed
 - Getting items from an `Interval` using a slice does no longer return a `list` but an `Interval` instance.
 - Intervals are properly pretty-printed by `pandas` ([#54](https://github.com/AlexandreDecan/portion/pull/54)).



## 2.1.4 (2020-11-26)

### Changed
 - Much faster `get`, `copy` and `|` operations for `IntervalDict`.



## 2.1.3 (2020-09-18)

### Fixed
 - Empty intervals are contained in all intervals ([#41](https://github.com/AlexandreDecan/portion/issues/41)).



## 2.1.2 (2020-09-16)

### Added
 - `IntervalDict` supports `|` and `|=`, the same way `dict` will do starting from Python 3.9 ([#37](https://github.com/AlexandreDecan/portion/issues/37)).

### Fixed
 - Fix invalid simplification of 3+ intervals when a closed interval shares the lower bound of an open one ([#38](https://github.com/AlexandreDecan/portion/issues/38)).
 - Fix the order in which items are returned from an `IntervalDict` when a closed interval shares the lower bound of an open one ([#39](https://github.com/AlexandreDecan/portion/issues/39)).



## 2.1.1 (2020-08-21)

### Fixed
 - Fix a regression introduced in 2.1.0 for `IntervalDict` ([#36](https://github.com/AlexandreDecan/portion/issues/36)).



## 2.1.0 (2020-08-09)

### Added
 - `IntervalDict.as_dict()` to export its content to a classical Python `dict`.

### Changed
 - `IntervalDict.keys()`, `values()` and `items()` return view objects instead of lists.

### Fixed
 - `IntervalDict.popitem()` now returns a (key, value) pair instead of an `IntervalDict`.
 - The documentation of `IntervalDict.pop()` now correctly states that the value (and not the key)
 is returned.



## 2.0.2 (2020-05-09)

### Fixed
 - Fix occasional `StopIteration` exception when checking for containment ([#28](https://github.com/AlexandreDecan/portion/issues/28)).


## 2.0.1 (2020-03-15)

### Fixed
 - Fix invalid representations of non-atomic intervals composed of a singleton ([#22](https://github.com/AlexandreDecan/portion/issues/22)).


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
 - (breaking) `AtomicInterval` is a `namedtuple` and is no longer part of the public API.
 - (breaking) Remove `i.to_atomic()` (use `i.enclosure` instead).
 - (breaking) Remove `i.is_empty()` (use `i.empty` instead).
 - (breaking) Remove `i.is_atomic()` (use `i.atomic` instead).
 - (breaking) `CLOSED` and `OPEN` do no longer define an implicit Boolean value. Use `~` instead of `not` to invert a bound.
 - (breaking) Remove deprecated `permissive` in `i.overlaps`.
 - (breaking) Remove `adjacent` in `i.overlaps`, use `i.adjacent` method instead.

### Fixed
 - Fix an issue where an interval can be composed of duplicated empty intervals ([#19](https://github.com/AlexandreDecan/portion/issues/19)).
 - Fix performance issues when intervals composed of hundreds of atomic intervals are complemented ([#20](https://github.com/AlexandreDecan/portion/issues/21))


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
