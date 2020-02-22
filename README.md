# Python data structure and operations for intervals

[![Travis](https://travis-ci.org/AlexandreDecan/python-intervals.svg?branch=master)](https://travis-ci.org/AlexandreDecan/python-intervals)
[![Coverage Status](https://coveralls.io/repos/github/AlexandreDecan/python-intervals/badge.svg?branch=master)](https://coveralls.io/github/AlexandreDecan/python-intervals?branch=master)
[![PyPI](https://badge.fury.io/py/python-intervals.svg)](https://pypi.org/project/python-intervals)


This library provides data structure and operations for intervals in Python 3.5+.

  * [Features](#features)
  * [Installation](#installation)
  * [Documentation & usage](#documentation--usage)
      * [Interval creation](#interval-creation)
      * [Interval operations](#interval-operations)
      * [Comparison operators](#comparison-operators)
      * [Bounds of an interval](#bounds-of-an-interval)
      * [Interval transformation](#interval-transformation)
      * [Discrete iteration](#discrete-iteration)
      * [Map intervals to data](#map-intervals-to-data)
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
 - Support comparison, transformation, intersection, union, complement, difference and containment.
 - Discrete iterations on the values of an interval.
 - Import and export intervals to strings and to Python built-in data types.
 - Dict-like structure to map intervals to data.
 - Heavily tested with high code coverage.


## Installation

You can use `pip` to install it, as usual: `pip install python-intervals`.

This will install the latest available version from [PyPI](https://pypi.org/project/python-intervals).
Pre-releases are available from the *master* branch on [GitHub](https://github.com/AlexandreDecan/python-intervals)
and can be installed with `pip install git+https://github.com/AlexandreDecan/python-intervals`.


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


[&uparrow; back to top](#python-data-structure-and-operations-for-intervals)
### Interval operations

`Interval` instances support the following operations:

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
 It supports intervals and arbitrary comparable values.
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


Intervals can also be iterated to access the underlying atomic intervals, sorted by their lower and upper bounds.

```python
>>> list(I.open(2, 3) | I.closed(0, 1) | I.closed(21, 24))
[[0,1], (2,3), [21,24]]

```

These atomic intervals can also be accessed using their indexes:

```python
>>> (I.open(2, 3) | I.closed(0, 1) | I.closed(21, 24))[0]
[0,1]
>>> (I.open(2, 3) | I.closed(0, 1) | I.closed(21, 24))[-2]
(2,3)

```


[&uparrow; back to top](#python-data-structure-and-operations-for-intervals)
### Comparison operators

Equality between intervals can be checked with the classical `==` operator:

```python
>>> I.closed(0, 2) == I.closed(0, 1) | I.closed(1, 2)
True
>>> I.closed(0, 2) == I.closed(0, 2).to_atomic()
True

```

Moreover, intervals are comparable using e.g. `>`, `>=`, `<` or `<=`.
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

Finally, intervals are hashable as long as their bounds are hashable (`I.inf` and `-I.inf` have a hash value).


[&uparrow; back to top](#python-data-structure-and-operations-for-intervals)
### Bounds of an interval

The left and right boundaries, and the lower and upper bounds of an interval can be respectively accessed
with its `left`, `right`, `lower` and `upper` attributes.
The `left` and `right` bounds are either `I.CLOSED` (`True`) or `I.OPEN` (`False`).

```python
>> I.CLOSED, I.OPEN
True, False
>>> x = I.closedopen(0, 1)
>>> x.left, x.lower, x.upper, x.right
(True, 0, 1, False)

```

If the interval is not atomic, then `left` and `lower` refer to the lower bound of its enclosure,
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

Intervals are immutable but provide a `replace` method to create a new interval based on the
current one. This method accepts four optional parameters `left`, `lower`, `upper`, and `right`:

```python
>>> i = I.closed(0, 2)
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

When `replace` is applied on an interval that is not atomic, it is extended and/or restricted such that
its enclosure satisfies the new bounds.

```python
>>> i = I.openclosed(0, 1) | I.closed(5, 10)
>>> i.replace(I.CLOSED, -1, 8, I.OPEN)
[-1,1] | [5,8)
>>> i.replace(lower=4)
(4,10]

```


[&uparrow; back to top](#python-data-structure-and-operations-for-intervals)
### Interval transformation

To apply an arbitrary transformation on an interval, intervals expose an `apply` method.
This method accepts a function that will be applied on each of the underlying atomic intervals to perform the desired transformation.
The function is expected to return either an `AtomicInterval`, an `Interval` or a 4-uple `(left, lower, upper, right)`.

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


[&uparrow; back to top](#python-data-structure-and-operations-for-intervals)
### Discrete iteration

The `iterate` function takes an interval, and returns a generator to iterate over
the values of an interval. Obviously, as intervals are continuous, it is required to specify the increment
 `incr` between consecutive values. The iteration then starts from the lower bound and ends on the upper one,
given they are not excluded by the interval:

```python
>>> list(I.iterate(I.closed(0, 3), incr=1))
[0, 1, 2, 3]
>>> list(I.iterate(I.closed(0, 3), incr=2))
[0, 2]
>>> list(I.iterate(I.open(0, 3), incr=2))
[2]

```

When an interval is not atomic, `iterate` consecutively iterates on all underlying atomic
intervals, starting from each lower bound and ending on each upper one:

```python
>>> list(I.iterate(I.singleton(0) | I.singleton(1) | I.singleton(5), incr=2))  # Won't be [0]
[0, 1, 5]
>>> list(I.iterate(I.closed(0, 2) | I.closed(5, 6), incr=3))  # Won't be [0, 6]
[0, 5]

```

Iteration can be performed in reverse order by specifying `reverse=True`. In that case, `incr` will be
subtracted instead of being added, implying that `incr` must always be a "positive" value:

```python
>>> list(I.iterate(I.closed(0, 3), incr=1, reverse=True))  # Not incr=-1
[3, 2, 1, 0]
>>> list(I.iterate(I.closed(0, 3), incr=2, reverse=True))  # Not incr=-2
[3, 1]

```

Again, this library does not make any assumption about the objects being used in an interval, as long as they
are comparable. However, it is not always possible to provide a meaningful value for `incr` (e.g., what would
be the step between two consecutive characters?). In these cases, a callable can be passed instead of a value.
This callable will be called with the current value, and is expected to return the next possible value.

```python
>>> list(I.iterate(I.closed('a', 'd'), incr=lambda d: chr(ord(d) + 1)))
['a', 'b', 'c', 'd']
>>> # Notice the reversed order, mind the "- 1"
>>> list(I.iterate(I.closed('a', 'd'), incr=lambda d: chr(ord(d) - 1), reverse=True))
['d', 'c', 'b', 'a']

```

By default, the iteration always starts on the lower bound (unless `reverse=True`) of each atomic interval.
The `base` parameter can be used to change this behaviour, by specifying how the initial value to start
the iteration on must be computed. This parameter accepts a callable that will be called with the lower
bound (unless `reverse=True`) for each underlying atomic interval, and that must return the first value to
consider instead of the lower bound.

This can be helpful to deal with (semi-)infinite intervals, or to *align* the generated values of
the iterator:

```python
>>> # Restrict values of a (semi-)infinite interval
>>> list(I.iterate(I.openclosed(-I.inf, 2), incr=1, base=lambda x: max(0, x)))
[0, 1, 2]
>>> # Align on integers
>>> list(I.iterate(I.closed(0.3, 4.9), incr=1, base=int))
[1, 2, 3, 4]

```

The `base` parameter can be used to change how `iterate` applies on unions of atomic interval, by
specifying a function that returns a single value, as illustrated next:

```python
>>> interval = I.closed(0, 1) | I.closed(2, 4) | I.closed(5, 6)
>>> list(I.iterate(interval, incr=3))  # Won't be [0, 3, 6]
[0, 2, 5]
>>> list(I.iterate(interval, incr=3, base=lambda x: 0))
[0, 3, 6]

```

Notice that this approach can be extremely inefficient in terms of performance when the intervals
are "far apart" each other.


[&uparrow; back to top](#python-data-structure-and-operations-for-intervals)
### Map intervals to data

The library provides an `IntervalDict` class, a `dict`-like data structure to store and query data
along with intervals. Any value can be stored in such data structure as long as it supports
equality.


```python
>>> d = I.IntervalDict()
>>> d[I.closed(0, 3)] = 'banana'
>>> d[4] = 'apple'
>>> d
{[0,3]: 'banana', [4]: 'apple'}

```

When a value is defined for an interval that overlaps an existing one, it is automatically updated
to take the new value into account:

```python
>>> d[I.closed(2, 4)] = 'orange'
>>> d
{[0,2): 'banana', [2,4]: 'orange'}

```

An `IntervalDict` can be queried using single values or intervals. If a single value is used as a
key, its behaviour corresponds to the one of a classical `dict`:

```python
>>> d[2]
'orange'
>>> d[5]  # Key does not exist
Traceback (most recent call last):
 ...
KeyError: 5
>>> d.get(5, default=0)
0

```

When an interval is used as a key, a new `IntervalDict` containing the values
for that interval is returned:

```python
>>> d[~I.empty()]  # Get all values, similar to d.copy()
{[0,2): 'banana', [2,4]: 'orange'}
>>> d[I.closed(1, 3)]
{[1,2): 'banana', [2,3]: 'orange'}
>>> d[I.closed(-2, 1)]
{[0,1]: 'banana'}
>>> d[I.closed(-2, -1)]
{}

```

By using `.get`, a default value (defaulting to `None`) can be specified.
This value is used to "fill the gaps" if the queried interval is not completely
covered by the `IntervalDict`:

```python
>>> d.get(I.closed(-2, 1), default='peach')
{[-2,0): 'peach', [0,1]: 'banana'}
>>> d.get(I.closed(-2, -1), default='peach')
{[-2,-1]: 'peach'}
>>> d.get(I.singleton(1), default='peach')  # Key is covered, default is not used
{[1]: 'banana'}

```

For convenience, an `IntervalDict` provides a way to look for specific data values.
The `.find` method always returns a (possibly empty) `Interval` instance for which given
value is defined:

```python
>>> d.find('banana')
[0,2)
>>> d.find('orange')
[2,4]
>>> d.find('carrot')
()

```

The active domain of an `IntervalDict` can be retrieved with its `.domain` method.
This method always returns a single `Interval` instance, where `.keys` returns a list
of disjoint intervals, one for each stored value.

```python
>>> d.domain()
[0,4]
>>> d.keys()
[[0,2), [2,4]]
>>> d.values()
['banana', 'orange']
>>> d.items()
[([0,2), 'banana'), ([2,4], 'orange')]

```

Two `IntervalDict` instances can be combined together using the `.combine` method.
This method returns a new `IntervalDict` whose keys and values are taken from the two
source `IntervalDict`. Values corresponding to non-intersecting keys are simply copied,
while values corresponding to intersecting keys are combined together using the provided
function, as illustrated hereafter:

```python
>>> d1 = I.IntervalDict({I.closed(0, 2): 'banana'})
>>> d2 = I.IntervalDict({I.closed(1, 3): 'orange'})
>>> concat = lambda x, y: x + '/' + y
>>> d1.combine(d2, how=concat)
{[0,1): 'banana', [1,2]: 'banana/orange', (2,3]: 'orange'}

```

Resulting keys always correspond to an outer join. Other joins can be easily simulated
by querying the resulting `IntervalDict` as follows:

```python
>>> d = d1.combine(d2, how=concat)
>>> d[d1.domain()]  # Left join
{[0,1): 'banana', [1,2]: 'banana/orange'}
>>> d[d2.domain()]  # Right join
{[1,2]: 'banana/orange', (2,3]: 'orange'}
>>> d[d1.domain() & d2.domain()]  # Inner join
{[1,2]: 'banana/orange'}

```

Finally, similarly to a `dict`, an `IntervalDict` also supports `len`, `in` and `del`, and defines
`.clear`, `.copy`, `.update`, `.pop`, `.popitem`, and `.setdefault`.


[&uparrow; back to top](#python-data-structure-and-operations-for-intervals)
### Import & export intervals to strings

Intervals can be exported to string, either using `repr` (as illustrated above) or with the `to_string` function.

```python
>>> I.to_string(I.closedopen(0, 1))
'[0,1)'

```

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


[&uparrow; back to top](#python-data-structure-and-operations-for-intervals)
### Import & export intervals to Python built-in data types

Intervals can also be exported to a list of 4-uples with `to_data`, e.g., to support JSON serialization.

```python
>>> x = I.openclosed(0, 1) | I.closedopen(2, I.inf)
>>> I.to_data(x)
[(False, 0, 1, True), (True, 2, inf, False)]

```

The function to convert bounds can be specified with the `conv` parameter.
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


[&uparrow; back to top](#python-data-structure-and-operations-for-intervals)
## Contributions

Contributions are very welcome!
Feel free to report bugs or suggest new features using GitHub issues and/or pull requests.


## Licence

Distributed under [LGPLv3 - GNU Lesser General Public License, version 3](https://github.com/AlexandreDecan/python-intervals/blob/master/LICENSE.txt).

You can refer to this library using:

```
@software{python-intervals,
  author = {Decan, Alexandre},
  title = {python-intervals: Python data structure and operations for intervals},
  url = {https://github.com/AlexandreDecan/python-intervals},
}
```


## Changelog

This library adheres to a [semantic versioning](https://semver.org) scheme.


**2.0.0-pre1** (not yet released)

 - Infinities define a hash value.
 - An interval is hashable if and only if is bounds are hashable.
 - Fix an issue where an interval can be made of duplicated empty intervals ([#19](https://github.com/AlexandreDecan/python-intervals/issues/19)).
 - Drop support for Python 2.7 and 3.4 since they reached end-of-life.
 - Breaking change: many (optional) parameters are converted to keyword-only arguments:
   * for `from_string` and `to_string`: `bound`, `disj`, `sep`, `left_open`, `left_closed`, `right_open`, `right_closed`, `pinf` and `ninf`;
   * for `from_data` and `to_data`: `pinf` and `ninf`;
   * for `iterate`: `base` and `reverse`;
   * for `i.replace`: `ignore_inf`;
   * for `i.overlaps`: `adjacent`.
 - Breaking change: remove deprecated `permissive` in `.overlaps` (use `adjacent` instead).
 - Restructure package in modules instead of a flat file.
 - Reorganise tests in modules and classes instead of a flat file.


**1.10.0** (2019-09-26)

 - `IntervalDict` has a `.combine` method to merge its keys and values with another `IntervalDict`.


**1.9.0** (2019-09-13)

 - Discrete iteration on the values of an interval with `iterate`.
 - Map intervals to data with the dict-like `IntervalDict` structure.
 - Faster comparisons between arbitrary values and intervals.
 - Deprecate `permissive` in `.overlaps` in favour of `adjacent`.
 - Fix `.union` when intervals share a bound, one inclusive and one exclusive ([#12](https://github.com/AlexandreDecan/python-intervals/issues/12)).
 - Fix `.overlaps` when intervals share a lower bound, and one interval is contained within the other one ([#13](https://github.com/AlexandreDecan/python-intervals/issues/13)).


**1.8.0** (2018-12-15)

 - Intervals have a `.left`, `.lower`, `.upper`, and `.right` attribute that refer to its enclosure.
 - Intervals have a `.replace` method to create new intervals based on the current one. This method accepts both values and functions.
 - Intervals have an `.apply` method to apply a function on the underlying atomic intervals.
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
