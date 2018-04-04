

# Interval arithmetic for Python

[![Travis](https://travis-ci.org/AlexandreDecan/python-intervals.svg?branch=master)](https://travis-ci.org/AlexandreDecan/python-intervals)
[![Coverage Status](https://coveralls.io/repos/github/AlexandreDecan/python-intervals/badge.svg?branch=master)](https://coveralls.io/github/AlexandreDecan/python-intervals?branch=master)
[![PyPi](https://badge.fury.io/py/python-intervals.svg)](https://pypi.org/project/python-intervals)


Provide interval arithmetic for Python 3.4+.


## Features

 - Support intervals of any (comparable) objects.
 - Closed or open, finite or infinite intervals.
 - Union of intervals out of the box.
 - Automatic simplification of (union of) intervals.
 - Support iteration, comparison, intersection, union, complement, difference and containment.


## Installation

You can use ``pip`` to install this library:

``pip install python-intervals``

This will install the latest available version from *pypi* branch.
Prereleases are available from the *master* branch.


## Usage

Assuming this library is imported using ``import intervals as I``, intervals can be easily created using one of the following functions:

 - ``I.open(1, 2)`` corresponds to ``(1,2)``;
 - ``I.closed(1, 2)`` corresponds to ``[1,2]``;
 - ``I.openclosed(1, 2)`` corresponds to ``(1,2]``;
 - ``I.closedopen(1, 2)`` corresponds to ``[1,2)``;
 - ``I.singleton(1)`` corresponds to ``[1,1]``;
 - ``I.empty()`` corresponds to the empty interval ``()``.

```python
>>> I.closed(0, 3)
[0,3]
>>> I.openclosed('a', 'z')
('a','z']
>>> I.singleton(2.5)
[2.5]
>>> I.empty()
()
```

Infinite and semi-infinite intervals are supported using ``I.inf`` and ``-I.inf`` as upper or lower bounds. These two objects support comparison with any other object.

```python
>>> I.openclosed(-I.inf, 0)
(-inf,0]
>>> I.closed(-I.inf, I.inf)  # Automatically converted
(-inf,+inf)
>>> I.inf > 'a', I.inf > 0, I.inf > True
(True, True, True)
```

Intervals created with this library are ``Interval`` instances.
An ``Interval`` object is a disjunction of ``AtomicInterval``.
An ``AtomicInterval`` represents a single interval (e.g. ``[1,2])`` while an ``Interval`` represents union of intervals (e.g. ``[1,2] | [3,4]``).


For convenience, ``Interval`` are automatically simplified:
```python
>>> I.closed(0, 2) | I.closed(2, 4)
[0,4]
>>> I.closed(1, 2) | I.closed(3, 4) | I.closed(2, 3)
[1,4]
>>> I.closed(1, 2) | I.openclosed(2, 3) | I.closedopen(5, 5)
[1,3]
```

Both classes support interval arithmetic:


 - ``x.intersection(other)`` or ``x & other`` returns the intersection of two intervals.
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
 - ``x.union(other)`` or ``x | other`` returns the union of two intervals.
   ```python
   >>> I.closed(0, 1) | I.closed(1, 2)
   [0,2]
   >>> I.closed(0, 1) | I.closed(2, 3)
   [0,1] | [2,3]
   ```
 - ``x.complement(other)`` or ``~x`` returns the complement of the interval.
   ```python
   >>> ~I.closed(0, 1)
   (-inf,0) | (1,+inf)
   >>> ~(I.open(-I.inf, 0) | I.open(1, I.inf))
   [0,1]
   >>> ~I.open(-I.inf, I.inf)
   ()
   ```
 - ``x.difference(other)`` or ``x - other`` returns the difference between ``x`` and ``other``.
   ```python
   >>> I.closed(0,2) - I.closed(1,2)
   [0,1)
   >>> I.closed(0, 4) - I.closed(1, 2)
   [0,1) | (2,4]
   ```
 - ``x == other`` checks for interval equality.
   ```python
   >>> I.closed(0, 2) == I.closed(0, 1) | I.closed(1, 2)
   True
   ```
 - ``x.is_empty()`` tests if the interval is empty.
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
 - ``x.overlaps(other)`` test if there is an overlap between two intervals. This method accepts a ``permissive`` parameter which defaults to ``False``. If ``True``, it considers that [1, 2) and [2, 3] have an overlap on 2 (but not [1, 2) and (2, 3]).
   ```python
   >>> I.closed(1, 2).overlaps(I.closed(2, 3))
   True
   >>> I.closed(1, 2).overlaps(I.open(2, 3))
   False
   >>> I.closed(1, 2).overlaps(I.open(2, 3), permissive=True)
   True
   ```
 - ``x.contains(other)`` or ``other in x`` returns True if given item is contained in the interval. Support ``Interval``, ``AtomicInterval`` and arbitrary comparable values.
   ```python
   >>> 2 in I.closed(0, 2)
   True
   >>> 2 in I.open(0, 2)
   False
   >> I.open(0, 1) in I.closed(0, 2)
   True
   ```

Moreover, both ``Interval`` and ``AtomicInterval`` are comparable using ``>`` or ``<``.
The comparison is based on the interval, not only on one bound or the other.
For instance, assuming ``a`` and ``b`` are intervals, ``a < b`` holds iff ``a`` is entirely lower than ``b``.

```python
>>> I.closed(0, 2) < I.closed(3, 4)
True
>>> I.closed(0, 2) < I.closed(2, 3)
False
```

While less meaningful, ``<=`` and ``>=`` are supported too and correspond exactly to ``< or ==`` (resp. ``> or ==``).
Consequently, comparisons between partially overlapping intervals will always evaluate to ``False``.

```python
>>> I.closed(0, 2) <= I.closed(2, 3)
False
>>> I.closed(0, 2) < I.closed(0, 2)
False
>>> I.closed(0, 2) | I.closed(5, 6) <= I.closed(3, 4)
False
>>> I.closed(0, 2) <= I.closed(0, 2)
True
```


Additionally, an ``Interval`` provides:

 - ``x.enclosure()`` returns the smallest interval that includes the current one.
   ```python
   >>> (I.closed(0, 1) | I.closed(2, 3)).enclosure()
   [0,3]
   ```
 - ``x.is_atomic()`` evaluates to ``True`` if interval is the union of a single (possibly empty) atomic interval.
   ```python
   >>> I.closed(0, 2).is_atomic(), (I.closed(0, 1) | I.closed(2, 3)).is_atomic()
   (True, False)
   ```
 - ``x.to_atomic()`` returns the smallest ``AtomicInterval`` that contains the interval(s). Is equivalent to ``x.enclosure()``
 but returns an ``AtomicInterval`` instead of an ``Interval`` object.


Intervals can be iterated to access the underlying set of ``AtomicInterval``, sorted by their lower bounds.
As intervals are automatically simplified, this implies their upper bounds are also sorted.

```python
>>> list(I.open(2, 3) | I.closed(0, 1) | I.closed(21, 24))
[[0,1], (2,3), [21,24]]
```

The ``AtomicInterval`` of an ``Interval`` can also be accessed using their index.

```python
>>> (I.open(2, 3) | I.closed(0, 1) | I.closed(21, 24))[-2]
(2,3)
```

The left and right boundaries, and the lower and upper bound of an ``AtomicInterval`` can be respectively accessed
with its ``left``, ``right``, ``lower`` and ``upper`` attribute.

```python
>>> [(i.left, i.lower, i.upper, i.right) for i in I.open(2, 3) | I.closed(0, 1)]
[(True, 0, 1, True), (False, 2, 3, False)]
```

## Contributions

Contributions are very welcome!
Feel free to report bugs or suggest new features using GitHub issues and/or pull requests.

This library was inspired by [pyinter](https://github.com/intiocean/pyinter).


## Licence

LGPLv3 - GNU Lesser General Public License, version 3


## Changelog

**1.2.0** (2018-04-04)

 - ``Interval`` support indexing, to retrieve the underlying ``AtomicInterval``.


**1.1.0** (2018-04-04)

 - Both ``AtomicInterval`` and ``Interval`` are fully comparable.
 - Add ``singleton(x)`` to create a singleton interval [x].
 - Add ``empty()`` to create an empty interval.
 - Add ``Interval.enclosure()`` that returns the smallest interval that includes the current one.
 - Interval simplification is in O(n) instead of O(n*m).
 - ``AtomicInterval`` in an ``Interval`` are sorted by lower bound.


**1.0.4** (2018-04-03)

 - All operations of ``AtomicInterval`` (except overlaps) accept ``Interval``.
 - Raise ``TypeError`` instead of ``ValueError`` if type is not supported (coherent with ``NotImplemented``).


**1.0.3** (2018-04-03)

 - Initial working release on PyPi.


**1.0.0** (2018-04-03)

 - Initial release.
