# Interval operations for Python

[![Travis](https://travis-ci.org/AlexandreDecan/python-intervals.svg?branch=master)](https://travis-ci.org/AlexandreDecan/python-intervals)
[![Coverage Status](https://coveralls.io/repos/github/AlexandreDecan/python-intervals/badge.svg?branch=master)](https://coveralls.io/github/AlexandreDecan/python-intervals?branch=master)
[![PyPI](https://badge.fury.io/py/python-intervals.svg)](https://pypi.org/project/python-intervals)


This library provides data structure and operations for intervals in Python 2.7+ and Python 3.4+.

  * [Features](#features)
  * [Installation](#installation)
  * [Documentation & usage](#documentation--usage)
      * [Interval creation](#interval-creation)
      * [Interval operations](#interval-operations)
      * [Bounds of an interval](#bounds-of-an-interval)
      * [Interval transformation](#interval-transformation)
      * [Iteration & indexing](#iteration--indexing)
      * [Comparison operators](#comparison-operators)
      * [Import & export intervals to strings](#import--export-intervals-to-strings)
      * [Import & export intervals to Python built-in data types](#import--export-intervals-to-python-built-in-data-types)
  * [Contributions](#contributions)
  * [Licence](#licence)
  * [Changelog](#changelog)


## Features

 - Support intervals of any (comparable) objects.
 - Closed or open, finite or (semi-)infinite intervals.
 - Atomic intervals and interval sets are supported.
 - Automatic simplification of intervals.
 - Support iteration, comparison, transformation, intersection, union, complement, difference and containment.
 - Import and export intervals to strings and to Python built-in data types.


## Installation

You can use `pip` to install it, as usual: `pip install python-intervals`.

This will install the latest available version from [PyPI](https://pypi.org/project/python-intervals).
Prereleases are available from the *master* branch on [GitHub](https://github.com/AlexandreDecan/python-intervals).

For convenience, the library is contained within a single Python file, and can thus be easily integrated in other
projects without the need for an explicit dependency (hint: don't do that!).


## Documentation & usage

### Interval creation

Assuming this library is imported using `import intervals as I`, intervals can be easily created using one of the
following helpers:

```python
>>> I.open(1, 2)
(1,2)
>>> I.closed(1, 2)
[1,2]
>>> I.openclosed(1, 2)
(1,2]
>>> I.closedopen(1, 2)
[1,2)
>>> I.singleton(1)
[1]
>>> I.empty()
()

```

Intervals created with this library are `Interval` instances.
An `Interval` object is a disjunction of atomic intervals that represent single intervals (e.g. `[1,2]`) corresponding to `AtomicInterval` instances.
Except when atomic intervals are explicitly created or retrieved, only `Interval` instances are exposed.

The bounds of an interval can be any arbitrary values, as long as they are comparable:

```python
>>> I.closed(1.2, 2.4)
[1.2,2.4]
>>> I.closed('a', 'z')
['a','z']
>>> import datetime
>>> I.closed(datetime.date(2011, 3, 15), datetime.date(2013, 10, 10))
[datetime.date(2011, 3, 15),datetime.date(2013, 10, 10)]

```


Infinite and semi-infinite intervals are supported using `I.inf` and `-I.inf` as upper or lower bounds.
These two objects support comparison with any other object.
When infinities are used as a lower or upper bound, the corresponding boundary is automatically converted to an open one.

```python
>>> I.inf > 'a', I.inf > 0, I.inf > True
(True, True, True)
>>> I.openclosed(-I.inf, 0)
(-inf,0]
>>> I.closed(-I.inf, I.inf)  # Automatically converted to an open interval
(-inf,+inf)

```

Empty intervals always resolve to `(I.inf, -I.inf)`, regardless of the provided bounds:

```python
>>> I.empty() == I.open(I.inf, -I.inf)
True
>>> I.closed(4, 3) == I.open(I.inf, -I.inf)
True
>>> I.openclosed('a', 'a') == I.open(I.inf, -I.inf)
True

```

For convenience, intervals are automatically simplified:
```python
>>> I.closed(0, 2) | I.closed(2, 4)
[0,4]
>>> I.closed(1, 2) | I.closed(3, 4) | I.closed(2, 3)
[1,4]
>>> I.empty() | I.closed(0, 1)
[0,1]
>>> I.closed(1, 2) | I.closed(2, 3) | I.closed(4, 5)
[1,3] | [4,5]

```

Note that discrete intervals are **not** supported, e.g., combining `[0,1]` with `[2,3]` will **not** result
in `[0,3]` even if there is no integer between `1` and `2`.


### Interval operations

Both `Interval` and `AtomicInterval` support following interval operations:

 - `x.is_empty()` tests if the interval is empty.
   ```python
   >>> I.closed(0, 1).is_empty()
   False
   >>> I.closed(0, 0).is_empty()
   False
   >>> I.openclosed(0, 0).is_empty()
   True
   >>> I.empty().is_empty()
   True

   ```

 - `x.intersection(other)` or `x & other` return the intersection of two intervals.
   ```python
   >>> I.closed(0, 2) & I.closed(1, 3)
   [1,2]
   >>> I.closed(0, 4) & I.open(2, 3)
   (2,3)
   >>> I.closed(0, 2) & I.closed(2, 3)
   [2]
   >>> I.closed(0, 2) & I.closed(3, 4)
   ()

   ```

 - `x.union(other)` or `x | other` return the union of two intervals.
   ```python
   >>> I.closed(0, 1) | I.closed(1, 2)
   [0,2]
   >>> I.closed(0, 1) | I.closed(2, 3)
   [0,1] | [2,3]

   ```

 - `x.complement(other)` or `~x` return the complement of the interval.
   ```python
   >>> ~I.closed(0, 1)
   (-inf,0) | (1,+inf)
   >>> ~(I.open(-I.inf, 0) | I.open(1, I.inf))
   [0,1]
   >>> ~I.open(-I.inf, I.inf)
   ()

   ```

 - `x.difference(other)` or `x - other` return the difference between `x` and `other`.
   ```python
   >>> I.closed(0,2) - I.closed(1,2)
   [0,1)
   >>> I.closed(0, 4) - I.closed(1, 2)
   [0,1) | (2,4]

   ```

 - `x.contains(other)` or `other in x` return True if given item is contained in the interval.
 Support `Interval`, `AtomicInterval` and arbitrary comparable values.
   ```python
   >>> 2 in I.closed(0, 2)
   True
   >>> 2 in I.open(0, 2)
   False
   >>> I.open(0, 1) in I.closed(0, 2)
   True

   ```

 - `x.overlaps(other)` tests if there is an overlap between two intervals.
 This method accepts a `adjacent` parameter which defaults to `False`.
 If `True`, it accepts adjacent intervals as well (e.g., [1, 2) and [2, 3] but not
 [1, 2) and (2, 3]).
   ```python
   >>> I.closed(1, 2).overlaps(I.closed(2, 3))
   True
   >>> I.closed(1, 2).overlaps(I.open(2, 3))
   False
   >>> I.closed(1, 2).overlaps(I.openclosed(2, 3), adjacent=True)
   True
   >>> I.closedopen(1, 2).overlaps(I.openclosed(2, 3), adjacent=True)
   False

   ```


The following methods are only available for `Interval` instances:

 - `x.enclosure()` returns the smallest interval that includes the current one.
   ```python
   >>> (I.closed(0, 1) | I.closed(2, 3)).enclosure()
   [0,3]

   ```

 - `x.to_atomic()` is equivalent to `x.enclosure()` but returns an `AtomicInterval` instead of an `Interval` object.

 - `x.is_atomic()` evaluates to `True` if interval is composed of a single (possibly empty) atomic interval.
   ```python
   >>> I.closed(0, 2).is_atomic()
   True
   >>> (I.closed(0, 1) | I.closed(1, 2)).is_atomic()
   True
   >>> (I.closed(0, 1) | I.closed(2, 3)).is_atomic()
   False

   ```


### Bounds of an interval

The left and right boundaries, and the lower and upper bounds of an `AtomicInterval` can be respectively accessed
with its `left`, `right`, `lower` and `upper` attributes.
The `left` and `right` bounds are either `I.CLOSED` (`True`) or `I.OPEN` (`False`).

```python
>> I.CLOSED, I.OPEN
True, False
>>> x = I.closedopen(0, 1).to_atomic()
>>> x.left, x.lower, x.upper, x.right
(True, 0, 1, False)

```

Similarly, the bounds of an `Interval` instance can be accessed with its `left`, `right`,
`lower` and `upper` attributes. In that case, `left` and `lower` refer to the lower bound of its enclosure,
while `right` and `upper` refer to the upper bound of its enclosure:

```python
>>> x = I.open(0, 1) | I.closed(3, 4)
>>> x.left, x.lower, x.upper, x.right
(False, 0, 4, True)

```

One can easily check for some interval properties based on the bounds of an interval:

```python
>>> x = I.openclosed(-I.inf, 0)
>>> # Check that interval is left/right closed
>>> x.left == I.CLOSED, x.right == I.CLOSED
(False, True)
>>> # Check that interval is left/right bounded
>>> x.lower == -I.inf, x.upper == I.inf
(True, False)
>>> # Check for singleton
>>> x.lower == x.upper
False

```


Both `Interval` and `AtomicInterval` instances are immutable but provide a `replace` method that
can be used to create a new instance based on the current one. This method accepts four optional
parameters `left`, `lower`, `upper`, and `right`:

```python
>>> i = I.closed(0, 2).to_atomic()
>>> i.replace(I.OPEN, -1, 3, I.CLOSED)
(-1,3]
>>> i.replace(lower=1, right=I.OPEN)
[1,2)

```

Functions can be passed instead of values. If a function is passed, it is called with the current corresponding
value except if the corresponding bound is an infinity and parameter `ignore_inf` if set to `False`.

```python
>>> I.closed(0, 2).replace(upper=lambda x: 2 * x)
[0,4]
>>> i = I.closedopen(0, I.inf)
>>> i.replace(upper=lambda x: 10)  # No change, infinity is ignored
[0,+inf)
>>> i.replace(upper=lambda x: 10, ignore_inf=False)  # Infinity is not ignored
[0,10)

```

When `replace` is applied on an `Interval` that is not atomic, it is extended and/or restricted such that
its enclosure satisfies the new bounds.

```python
>>> i = I.openclosed(0, 1) | I.closed(5, 10)
>>> i.replace(I.CLOSED, -1, 8, I.OPEN)
[-1,1] | [5,8)
>>> i.replace(lower=4)
(4,10]

```


### Interval transformation

To apply an arbitrary transformation on an interval, `Interval` instances expose an `apply` method.
This method accepts a function that will be applied on each of the underlying atomic intervals to perform the desired transformation.
The function is expected to return an `AtomicInterval`, an `Interval` or a 4-uple `(left, lower, upper, right)`.

```python
>>> i = I.closed(2, 3) | I.open(4, 5)
>>> # Increment bound values
>>> i.apply(lambda x: (x.left, x.lower + 1, x.upper + 1, x.right))
[3,4] | (5,6)
>>> # Invert bounds
>>> i.apply(lambda x: (not x.left, x.lower, x.upper, not x.right))
(2,3) | [4,5]

```

The `apply` method is very powerful when used in combination with `replace`.
Because the latter allows functions to be passed as parameters and can ignore infinities, it can be
conveniently used to transform intervals in presence of infinities.

```python
>>> i = I.openclosed(-I.inf, 0) | I.closed(3, 4) | I.closedopen(8, I.inf)
>>> # Increment bound values
>>> i.apply(lambda x: x.replace(upper=lambda v: v + 1))
(-inf,1] | [3,5] | [8,+inf)
>>> # Intervals are still automatically simplified
>>> i.apply(lambda x: x.replace(lower=lambda v: v * 2))
(-inf,0] | [16,+inf)
>>> # Invert bounds
>>> i.apply(lambda x: x.replace(left=lambda v: not v, right=lambda v: not v))
(-inf,0) | (3,4) | (8,+inf)
>>> # Replace infinities with -10 and 10
>>> conv = lambda v: -10 if v == -I.inf else (10 if v == I.inf else v)
>>> i.apply(lambda x: x.replace(lower=conv, upper=conv, ignore_inf=False))
(-10,0] | [3,4] | [8,10)

```


### Iteration & indexing

Intervals can be iterated to access the underlying `AtomicInterval` objects, sorted by their lower and upper bounds.

```python
>>> list(I.open(2, 3) | I.closed(0, 1) | I.closed(21, 24))
[[0,1], (2,3), [21,24]]

```

The `AtomicInterval` objects of an `Interval` can also be accessed using their indexes:

```python
>>> (I.open(2, 3) | I.closed(0, 1) | I.closed(21, 24))[0]
[0,1]
>>> (I.open(2, 3) | I.closed(0, 1) | I.closed(21, 24))[-2]
(2,3)

```


### Comparison operators

Equality between intervals can be checked with the classical `==` operator:

```python
>>> I.closed(0, 2) == I.closed(0, 1) | I.closed(1, 2)
True
>>> I.closed(0, 2) == I.closed(0, 2).to_atomic()
True

```

Moreover, both `Interval` and `AtomicInterval` are comparable using e.g. `>`, `>=`, `<` or `<=`.
These comparison operators have a different behaviour than the usual ones.
For instance, `a < b` holds if `a` is entirely on the left of the lower bound of `b` and `a > b` holds if `a` is entirely
on the right of the upper bound of `b`.

```python
>>> I.closed(0, 1) < I.closed(2, 3)
True
>>> I.closed(0, 1) < I.closed(1, 2)
False

```

Similarly, `a <= b` holds if `a` is entirely on the left of the upper bound of `b`, and `a >= b`
holds if `a` is entirely on the right of the lower bound of `b`.

```python
>>> I.closed(0, 1) <= I.closed(2, 3)
True
>>> I.closed(0, 2) <= I.closed(1, 3)
True
>>> I.closed(0, 3) <= I.closed(1, 2)
False

```

Intervals can also be compared with single values. If `i` is an interval and `x` a value, then
`x < i` holds if `x` is on the left of the lower bound of `i` and `x <= i` holds if `x` is on the
left of the upper bound of `i`. This behaviour is similar to the one that could be obtained by first
converting `x` to a singleton interval.

```python
>>> 5 < I.closed(0, 10)
False
>>> 5 <= I.closed(0, 10)
True
>>> I.closed(0, 10) < 5
False
>>> I.closed(0, 10) <= 5
True

```


Note that all these semantics differ from classical comparison operators.
As a consequence, some intervals are never comparable in the classical sense, as illustrated hereafter:

```python
>>> I.closed(0, 4) <= I.closed(1, 2) or I.closed(0, 4) >= I.closed(1, 2)
False
>>> I.closed(0, 4) < I.closed(1, 2) or I.closed(0, 4) > I.closed(1, 2)
False
>>> I.empty() < I.empty()
True

```


### Import & export intervals to strings

Intervals can be exported to string, either using `repr` (as illustrated above) or with the `to_string` function.

```python
>>> I.to_string(I.closedopen(0, 1))
'[0,1)'

```

This function accepts both `Interval` and `AtomicInterval` instances.
The way string representations are built can be easily parametrized using the various parameters supported by
`to_string`:

```python
>>> params = {
...   'disj': ' or ',
...   'sep': ' - ',
...   'left_closed': '<',
...   'right_closed': '>',
...   'left_open': '..',
...   'right_open': '..',
...   'pinf': '+oo',
...   'ninf': '-oo',
...   'conv': lambda v: '"{}"'.format(v),
... }
>>> x = I.openclosed(0, 1) | I.closed(2, I.inf)
>>> I.to_string(x, **params)
'.."0" - "1"> or <"2" - +oo..'

```

Similarly, intervals can be created from a string using the `from_string` function.
A conversion function (`conv` parameter) has to be provided to convert a bound (as string) to a value.

```python
>>> I.from_string('[0, 1]', conv=int) == I.closed(0, 1)
True
>>> I.from_string('[1.2]', conv=float) == I.singleton(1.2)
True
>>> converter = lambda s: datetime.datetime.strptime(s, '%Y/%m/%d')
>>> I.from_string('[2011/03/15, 2013/10/10]', conv=converter)
[datetime.datetime(2011, 3, 15, 0, 0),datetime.datetime(2013, 10, 10, 0, 0)]

```

Similarly to `to_string`, function `from_string` can be parametrized to deal with more elaborated inputs.
Notice that as `from_string` expects regular expression patterns, we need to escape some characters.

```python
>>> s = '.."0" - "1"> or <"2" - +oo..'
>>> params = {
...   'disj': ' or ',
...   'sep': ' - ',
...   'left_closed': '<',
...   'right_closed': '>',
...   'left_open': r'\.\.',  # from_string expects regular expression patterns
...   'right_open': r'\.\.',  # from_string expects regular expression patterns
...   'pinf': r'\+oo',  # from_string expects regular expression patterns
...   'ninf': '-oo',
...   'conv': lambda v: int(v[1:-1]),
... }
>>> I.from_string(s, **params)
(0,1] | [2,+inf)

```

When a bound contains a comma or has a representation that cannot be automatically parsed with `from_string`,
the `bound` parameter can be used to specify the regular expression that should be used to match its representation.

```python
>>> s = '[(0, 1), (2, 3)]'  # Bounds are expected to be tuples
>>> I.from_string(s, conv=eval, bound=r'\(.+?\)')
[(0, 1),(2, 3)]

```


### Import & export intervals to Python built-in data types

Intervals can also be exported to a list of 4-uples with `to_data`, e.g., to support JSON serialization.

```python
>>> x = I.openclosed(0, 1) | I.closedopen(2, I.inf)
>>> I.to_data(x)
[(False, 0, 1, True), (True, 2, inf, False)]

```

The function that is used to convert bounds can be specified with the `conv` parameter.
The values that must be used to represent positive and negative infinities can be specified with
`pinf` and `ninf`. They default to `float('inf')` and `float('-inf')` respectively.

```python
>>> x = I.closed(datetime.date(2011, 3, 15), datetime.date(2013, 10, 10))
>>> I.to_data(x, conv=lambda v: (v.year, v.month, v.day))
[(True, (2011, 3, 15), (2013, 10, 10), True)]

```

Intervals can be imported from such a list of 4-uples with `from_data`.
The same set of parameters can be used to specify how bounds and infinities are converted.

```python
>>> x = [(True, (2011, 3, 15), (2013, 10, 10), False)]
>>> I.from_data(x, conv=lambda v: datetime.date(*v))
[datetime.date(2011, 3, 15),datetime.date(2013, 10, 10))

```


## Contributions

Contributions are very welcome!
Feel free to report bugs or suggest new features using GitHub issues and/or pull requests.


## Licence

Distributed under [LGPLv3 - GNU Lesser General Public License, version 3](https://github.com/AlexandreDecan/python-intervals/blob/master/LICENSE.txt).


## Changelog

This library adheres to a [semantic versioning](https://semver.org) scheme.

**Unreleased**

 - Deprecate `permissive` in `Interval.overlaps` in favour of `adjacent`.


**1.8.0** (2018-12-15)

 - Intervals have a `left`, `lower`, `upper`, and `right` attribute that refer to its enclosure.
 - Intervals have a `replace` method to create new intervals based on the current one. This method accepts both values and functions.
 - Intervals have an `apply` method to apply a function on the underlying atomic intervals.
 - Intervals can be compared with single values as well.
 - `I.empty()` returns the same instance to save memory.
 - Infinities are singleton objects.
 - Set `len(I.empty()) = 1` and `I.empty()[0] == I.empty().to_atomic()` for consistency.


**1.7.0** (2018-12-06)

 - Import from and export to Python built-in data types (a list of 4-uples) with `from_data` and `to_data` ([#6](https://github.com/AlexandreDecan/python-intervals/issues/6)).
 - Add examples for arbitrary interval transformations.


**1.6.0** (2018-08-29)

 - Add support for customized infinity representation in `to_string` and `from_string` ([#3](https://github.com/AlexandreDecan/python-intervals/issues/3)).


**1.5.4** (2018-07-29)

 - Fix `.overlaps` ([#2](https://github.com/AlexandreDecan/python-intervals/issues/2)).


**1.5.3** (2018-06-21)

 - Fix invalid `repr` for atomic singleton intervals.


**1.5.2** (2018-06-15)

 - Fix invalid comparisons when both `Interval` and `AtomicInterval` are compared.


**1.5.1** (2018-04-25)

 - Fix [#1](https://github.com/AlexandreDecan/python-intervals/issues/1) by making empty intervals always resolving to `(I.inf, -I.inf)`.


**1.5.0** (2018-04-17)

 - `Interval.__init__` accepts `Interval` instances in addition to `AtomicInterval` ones.


**1.4.0** (2018-04-17)

 - Function `I.to_string` to export an interval to a string, with many options to customize the representation.
 - Function `I.from_string` to create an interval from a string, with many options to customize the parsing.


**1.3.2** (2018-04-13)

 - Support for Python 2.7.


**1.3.1** (2018-04-12)

 - Define `__slots__` to lower memory usage, and to speed up attribute access.
 - Define `Interval.__rand__` (and other magic methods) to support `Interval` from `AtomicInterval` instead of
 having a dedicated piece of code in `AtomicInterval`.
 - Fix `__all__`.
 - More tests to cover all comparisons.


**1.3.0** (2018-04-04)

 - Meaningful `<=` and `>=` comparisons for intervals.


**1.2.0** (2018-04-04)

 - `Interval` supports indexing to retrieve the underlying `AtomicInterval` objects.


**1.1.0** (2018-04-04)

 - Both `AtomicInterval` and `Interval` are fully comparable.
 - Add `singleton(x)` to create a singleton interval [x].
 - Add `empty()` to create an empty interval.
 - Add `Interval.enclosure()` that returns the smallest interval that includes the current one.
 - Interval simplification is in O(n) instead of O(n*m).
 - `AtomicInterval` objects in an `Interval` are sorted by lower and upper bounds.


**1.0.4** (2018-04-03)

 - All operations of `AtomicInterval` (except overlaps) accept `Interval`.
 - Raise `TypeError` instead of `ValueError` if type is not supported (coherent with `NotImplemented`).


**1.0.3** (2018-04-03)

 - Initial working release on PyPi.


**1.0.0** (2018-04-03)

 - Initial release.
