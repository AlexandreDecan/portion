
# Interval arithmetic for Python

This repository contains the Python ``intervals`` library that provides basic arithmetic for intervals in Python, supporting arbitrary object type.

This library is inspired by [pyinter](https://github.com/intiocean/pyinter). Tested on Python3.5.

## Installation

Although distributed as a Python package, this library is not available on PyPi. To install it, use:

``pip install git+https://github.com/AlexandreDecan/python-intervals.git``


## Usage

Assuming this library is imported using ``import intervals as I``, intervals can be easily created using one of the following functions:

 - ``I.open(1, 2)`` corresponds to (1, 2);
 - ``I.closed(1, 2)`` corresponds to [1, 2];
 - ``I.openclosed(1, 2)`` corresponds to (1, 2];
 - and ``I.closedopen(1, 2)`` corresponds to [1, 2).

For convenience, we provide ``I.INF`` and ``-I.INF`` that can be used respectively as upper or lower bound, and that always evaluate to ``True`` when compared using ``<`` and ``>`` respectively, regardless of the type involved in the comparison.

An ``I.Interval`` is a disjunction of ``I.AtomicInterval``. An ``AtomicInterval`` represents a single interval (e.g. [1, 2]) while an ``Interval`` can also represent union of intervals (e.g. [1, 2] | [3, 4]). These unions are automatically simplified, e.g. [1, 2] | (2, 3] | (5, 5] automatically translates to [1, 3].

Both ``Interval`` and ``AtomicInterval`` support the following operations:

 - ``x.is_empty()`` tests if the interval is empty.
 - ``x.overlaps(other)`` test if there is an overlap between two intervals. This method accepts a ``permissive`` parameter which defaults to ``False``. If ``True``, it considers that [1, 2) and [2, 3] have an overlap on 2 (but not [1, 2) and (2, 3]).
 - ``x.intersection(other)`` or ``x & other`` returns the intersection of two intervals.
 - ``x.union(other)`` or ``x | other`` returns the union of two intervals.
 - ``x.contains(other)`` or ``other in x`` returns True if given item is contained in the interval. Support ``Interval``, ``AtomicInterval`` and arbitrary comparable values.
 - ``x == other`` checks for interval equality.

Additionally, an ``Interval`` provides:

 - ``x.is_atomic()`` evaluates to ``True`` if interval is the union of a single (possibly empty) atomic interval.
 - ``x.to_atomic()`` returns the smallest ``AtomicInterval`` that contains the interval(s).


## Examples

```python
>>> import intervals as I
>>> I.closed(0, 3)
[0,3]
>>> I.openclosed('a', 'z')
]'a','z']
>>> I.openclosed(-I.INF, 0)
]-inf,0]
>>> 2 in I.closed(0, 3)
True
>>> I.closed(0, 2) & I.open(1, 4)
]1,2]
>>> I.closed(0, 1) & I.closed(2, 3)
()
>>> I.closed(0, 2) | I.open(1, 4)
[0,4[
>>> I.closed(0, 1) | I.closed(2, 3) | I.closed(1, 2)
[0,3]
>>> I.closed(0, 1) | I.closed(2, 3)
[0,1] | [2,3]
```

## Contributions

Contributions are very welcome!
Feel free to report bugs or suggest new features using GitHub issues and/or pull requests.


## Licence

LGPLv3 - GNU Lesser General Public License, version 3
