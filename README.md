# Interval arithmetic for Python

[![Travis](https://travis-ci.org/AlexandreDecan/python-intervals.svg?branch=master)](https://travis-ci.org/AlexandreDecan/python-intervals)
[![Coverage Status](https://coveralls.io/repos/github/AlexandreDecan/python-intervals/badge.svg?branch=master)](https://coveralls.io/github/AlexandreDecan/python-intervals?branch=master)
[![PyPI](https://badge.fury.io/py/python-intervals.svg)](https://pypi.org/project/python-intervals)


This library provides interval arithmetic for Python 2.7+ and Python 3.4+.


## Features

 - Support intervals of any (comparable) objects.
 - Closed or open, finite or infinite intervals.
 - Atomic intervals and interval sets are supported.
 - Automatic simplification of intervals.
 - Support iteration, comparison, intersection, union, complement, difference and containment.


## Installation

You can use `pip` to install it, as usual: `pip install python-intervals`.

This will install the latest available version from [PyPI](https://pypi.org/project/python-intervals).
Prereleases are available from its *master* branch on [GitHub](https://github.com/AlexandreDecan/python-intervals).

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
Except when atomic intervals are explicitly created or retrieved, only `Interval` instances are exposed

The bounds of an interval can be any arbitrary values, as long as they are comparable:

```python
>>> I.closed(1.2, 2.4)
[1.2,2.4]
>>> I.closed('a', 'z')
['a','z']
>>> from datetime import date
>>> I.closed(date(2011, 3, 15), date(2013, 10, 10))
[datetime.date(2011, 3, 15),datetime.date(2013, 10, 10)]

```


Infinite and semi-infinite intervals are supported using `I.inf` and `-I.inf` as upper or lower bounds.
These two objects support comparison with any other object.
When infinites are used as a lower or upper bound, the corresponding boundary is automatically converted to an open one.

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




### Arithmetic operations

Both `Interval` and `AtomicInterval` support following interval arithmetic operations:

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
 This method accepts a `permissive` parameter which defaults to `False`. If `True`, it considers that [1, 2) and
 [2, 3] have an overlap on 2 (but not [1, 2) and (2, 3]).
   ```python
   >>> I.closed(1, 2).overlaps(I.closed(2, 3))
   True
   >>> I.closed(1, 2).overlaps(I.open(2, 3))
   False
   >>> I.closed(1, 2).overlaps(I.open(2, 3), permissive=True)
   True

   ```

### Other methods and attributes

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

The left and right boundaries, and the lower and upper bound of an `AtomicInterval` can be respectively accessed
with its `left`, `right`, `lower` and `upper` attributes.
The `left` and `right` bounds are either `I.CLOSED` (`True`) or `I.OPEN` (`False`).

```python
>> I.CLOSED, I.OPEN
True, False
>>> x = I.closedopen(0, 1).to_atomic()
>>> x.left, x.lower, x.upper, x.right
(True, 0, 1, False)

```


### Comparison operators

Equality between intervals can be checked using the classical `==` operator:

```python
>>> I.closed(0, 2) == I.closed(0, 1) | I.closed(1, 2)
True
>>> I.closed(0, 2) == I.closed(0, 2).to_atomic()
True

```

Moreover, both `Interval` and `AtomicInterval` are comparable using e.g. `>`, `>=`, `<` or `<=`.
The comparison is based on the interval itself, not on its lower or upper bound only.
For instance, `a < b` holds if `a` is entirely on the left of `b` and `a > b` holds if `a` is entirely
on the right of `b`.

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

Note that this semantics differ from classical comparison operators.
As a consequence, some intervals are never comparable in the classical sense, as illustrated hereafter:

```python
>>> I.closed(0, 4) <= I.closed(1, 2) or I.closed(0, 4) >= I.closed(1, 2)
False
>>> I.closed(0, 4) < I.closed(1, 2) or I.closed(0, 4) > I.closed(1, 2)
False
>>> I.empty() < I.empty()
True

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

### Import and export to string

Intervals can be exported to string, either using `repr` (as illustrated above) or with the `to_string` function.

```python
>>> I.to_string(I.closedopen(0, 1))
'[0,1)'

```

This function accepts both `Interval` and `AtomicInterval` instances.
The way string representations are built can be easily parametrized using the various parameters supported by
`to_string`:

```python
>>> x = I.openclosed(0, 1) | I.closed(2, I.inf)
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
>>> from datetime import datetime
>>> converter = lambda s: datetime.strptime(s, '%Y/%m/%d')
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



## Contributions

Contributions are very welcome!
Feel free to report bugs or suggest new features using GitHub issues and/or pull requests.


## Licence

Distributed under [LGPLv3 - GNU Lesser General Public License, version 3](https://github.com/AlexandreDecan/python-intervals/blob/master/LICENSE.txt).


## Changelog

This library adheres to a [semantic versioning](https://semver.org) scheme.


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
