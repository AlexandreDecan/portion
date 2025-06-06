# portion - data structure and operations for intervals

[![Tests](https://github.com/AlexandreDecan/portion/actions/workflows/test.yaml/badge.svg?branch=master)](https://github.com/AlexandreDecan/portion/actions/workflows/test.yaml)
[![Coverage Status](https://coveralls.io/repos/github/AlexandreDecan/portion/badge.svg?branch=master)](https://coveralls.io/github/AlexandreDecan/portion?branch=master)
[![License](https://badgen.net/pypi/license/portion)](https://github.com/AlexandreDecan/portion/blob/master/LICENSE.txt)
[![PyPI](https://badgen.net/pypi/v/portion)](https://pypi.org/project/portion)
[![Commits](https://badgen.net/github/last-commit/AlexandreDecan/portion)](https://github.com/AlexandreDecan/portion/commits/)


The `portion` library provides data structure and operations for intervals in Python.

 - Support intervals of any (comparable) objects.
 - Closed or open, finite or (semi-)infinite intervals.
 - Interval sets (union of atomic intervals) are supported.
 - Automatic simplification of intervals.
 - Support comparison, transformation, intersection, union, complement, difference and containment.
 - Provide test for emptiness, atomicity, overlap and adjacency.
 - Discrete iterations on the values of an interval.
 - Dict-like structure to map intervals to data.
 - Import and export intervals to strings and to Python built-in data types.
 - Heavily tested with high code coverage.


## Table of contents

  * [Installation](#installation)
  * [Documentation & usage](#documentation--usage)
      * [Interval creation](#interval-creation)
      * [Interval bounds & attributes](#interval-bounds--attributes)
      * [Interval operations](#interval-operations)
      * [Comparison operators](#comparison-operators)
      * [Interval transformation](#interval-transformation)
      * [Discrete iteration](#discrete-iteration)
      * [Map intervals to data](#map-intervals-to-data)
      * [Import & export intervals to strings](#import--export-intervals-to-strings)
      * [Import & export intervals to Python built-in data types](#import--export-intervals-to-python-built-in-data-types)
      * [Specialize & customize intervals](#specialize--customize-intervals)
  * [Changelog](#changelog)
  * [Contributions](#contributions)
  * [License](#license)


## Installation

You can use `pip` to install it, as usual: `pip install portion`. This will install the latest available version from [PyPI](https://pypi.org/project/portion).
Pre-releases are available from the *master* branch on [GitHub](https://github.com/AlexandreDecan/portion) and can be installed with `pip install git+https://github.com/AlexandreDecan/portion`.

You can install `portion` and its development environment using `pip install --group dev` at the root of this repository. This automatically installs [pytest](https://docs.pytest.org/en/latest/) (for the test suites) and [ruff](https://docs.astral.sh/ruff/) (for code style).


## Documentation & usage

### Interval creation

Assuming this library is imported using `import portion as P`, intervals can be easily created using one of the following helpers:

```python
>>> P.open(1, 2)
(1,2)
>>> P.closed(1, 2)
[1,2]
>>> P.openclosed(1, 2)
(1,2]
>>> P.closedopen(1, 2)
[1,2)
>>> P.singleton(1)
[1]
>>> P.empty()
()

```

The bounds of an interval can be any arbitrary values, as long as they are comparable:

```python
>>> P.closed(1.2, 2.4)
[1.2,2.4]
>>> P.closed('a', 'z')
['a','z']
>>> import datetime
>>> P.closed(datetime.date(2011, 3, 15), datetime.date(2013, 10, 10))
[datetime.date(2011, 3, 15),datetime.date(2013, 10, 10)]

```


Infinite and semi-infinite intervals are supported using `P.inf` and `-P.inf` as upper or lower bounds.
These two objects support comparison with any other object.
When infinities are used as a lower or upper bound, the corresponding boundary is automatically converted to an open one.

```python
>>> P.inf > 'a', P.inf > 0, P.inf > True
(True, True, True)
>>> P.openclosed(-P.inf, 0)
(-inf,0]
>>> P.closed(-P.inf, P.inf)  # Automatically converted to an open interval
(-inf,+inf)

```

Intervals created with this library are `Interval` instances.
An `Interval` instance is a disjunction of atomic intervals each representing a single interval (e.g. `[1,2]`).
Intervals can be iterated to access the underlying atomic intervals, sorted by their lower and upper bounds.

```python
>>> list(P.open(10, 11) | P.closed(0, 1) | P.closed(20, 21))
[[0,1], (10,11), [20,21]]
>>> list(P.empty())
[]

```

Nested (sorted) intervals can also be retrieved with a position or a slice:

```python
>>> (P.open(10, 11) | P.closed(0, 1) | P.closed(20, 21))[0]
[0,1]
>>> (P.open(10, 11) | P.closed(0, 1) | P.closed(20, 21))[-2]
(10,11)
>>> (P.open(10, 11) | P.closed(0, 1) | P.closed(20, 21))[:2]
[0,1] | (10,11)

```

For convenience, intervals are automatically simplified:

```python
>>> P.closed(0, 2) | P.closed(2, 4)
[0,4]
>>> P.closed(1, 2) | P.closed(3, 4) | P.closed(2, 3)
[1,4]
>>> P.empty() | P.closed(0, 1)
[0,1]
>>> P.closed(1, 2) | P.closed(2, 3) | P.closed(4, 5)
[1,3] | [4,5]

```

Note that, by default, simplification of discrete intervals is **not** supported by `portion` (but it can be simulated though, see [#24](https://github.com/AlexandreDecan/portion/issues/24#issuecomment-604456362)).
For example, combining `[0,1]` with `[2,3]` will **not** result in `[0,3]` even if there is no integer between `1` and `2`.
Refer to [Specialize & customize intervals](#specialize--customize-intervals) to see how to create and use specialized discrete intervals.



[&uparrow; back to top](#table-of-contents)
### Interval bounds & attributes


An `Interval` defines the following properties:

 - `i.empty` is `True` if and only if the interval is empty.
   ```python
   >>> P.closed(0, 1).empty
   False
   >>> P.closed(0, 0).empty
   False
   >>> P.openclosed(0, 0).empty
   True
   >>> P.empty().empty
   True

   ```

 - `i.atomic` is `True` if and only if the interval is empty or is a disjunction of a single interval.
   ```python
   >>> P.empty().atomic
   True
   >>> P.closed(0, 2).atomic
   True
   >>> (P.closed(0, 1) | P.closed(1, 2)).atomic
   True
   >>> (P.closed(0, 1) | P.closed(2, 3)).atomic
   False

   ```

 - `i.enclosure` refers to the smallest atomic interval that includes the current one.
   ```python
   >>> (P.closed(0, 1) | P.open(2, 3)).enclosure
   [0,3)

   ```

The left and right boundaries, and the lower and upper bounds of an interval can be respectively accessed with its `left`, `right`, `lower` and `upper` attributes.
The `left` and `right` bounds are either `P.CLOSED` or `P.OPEN`.
By definition, `P.CLOSED == ~P.OPEN` and vice-versa.

```python
>> P.CLOSED, P.OPEN
CLOSED, OPEN
>>> x = P.closedopen(0, 1)
>>> x.left, x.lower, x.upper, x.right
(CLOSED, 0, 1, OPEN)

```

By convention, empty intervals resolve to `(P.inf, -P.inf)`:

```python
>>> i = P.empty()
>>> i.left, i.lower, i.upper, i.right
(OPEN, +inf, -inf, OPEN)

```


If the interval is not atomic, then `left` and `lower` refer to the lower bound of its enclosure, while `right` and `upper` refer to the upper bound of its enclosure:

```python
>>> x = P.open(0, 1) | P.closed(3, 4)
>>> x.left, x.lower, x.upper, x.right
(OPEN, 0, 4, CLOSED)

```

One can easily check for some interval properties based on the bounds of an interval:

```python
>>> x = P.openclosed(-P.inf, 0)
>>> # Check that interval is left/right closed
>>> x.left == P.CLOSED, x.right == P.CLOSED
(False, True)
>>> # Check that interval is left/right bounded
>>> x.lower == -P.inf, x.upper == P.inf
(True, False)
>>> # Check for singleton
>>> x.lower == x.upper
False

```



[&uparrow; back to top](#table-of-contents)
### Interval operations

`Interval` instances support the following operations:

 - `i.intersection(other)` and `i & other` return the intersection of two intervals.
   ```python
   >>> P.closed(0, 2) & P.closed(1, 3)
   [1,2]
   >>> P.closed(0, 4) & P.open(2, 3)
   (2,3)
   >>> P.closed(0, 2) & P.closed(2, 3)
   [2]
   >>> P.closed(0, 2) & P.closed(3, 4)
   ()

   ```

 - `i.union(other)` and `i | other` return the union of two intervals.
   ```python
   >>> P.closed(0, 1) | P.closed(1, 2)
   [0,2]
   >>> P.closed(0, 1) | P.closed(2, 3)
   [0,1] | [2,3]

   ```

 - `i.complement(other)` and `~i` return the complement of the interval.
   ```python
   >>> ~P.closed(0, 1)
   (-inf,0) | (1,+inf)
   >>> ~(P.open(-P.inf, 0) | P.open(1, P.inf))
   [0,1]
   >>> ~P.open(-P.inf, P.inf)
   ()

   ```

 - `i.difference(other)` and `i - other` return the difference between `i` and `other`.
   ```python
   >>> P.closed(0,2) - P.closed(1,2)
   [0,1)
   >>> P.closed(0, 4) - P.closed(1, 2)
   [0,1) | (2,4]

   ```

 - `i.contains(other)` and `other in i` hold if given item is contained in the interval.
 It supports intervals and arbitrary comparable values.
   ```python
   >>> 2 in P.closed(0, 2)
   True
   >>> 2 in P.open(0, 2)
   False
   >>> P.open(0, 1) in P.closed(0, 2)
   True

   ```

 - `i.adjacent(other)` tests if the two intervals are adjacent, i.e., if they do not overlap and their union form a single atomic interval.
 While this definition corresponds to the usual notion of adjacency for atomic  intervals, it has stronger requirements for non-atomic ones since it requires  all underlying atomic intervals to be adjacent (i.e. that one  interval fills the gaps between the atomic intervals of the other one).
   ```python
   >>> P.closed(0, 1).adjacent(P.openclosed(1, 2))
   True
   >>> P.closed(0, 1).adjacent(P.closed(1, 2))
   False
   >>> (P.closed(0, 1) | P.closed(2, 3)).adjacent(P.open(1, 2) | P.open(3, 4))
   True
   >>> (P.closed(0, 1) | P.closed(2, 3)).adjacent(P.open(3, 4))
   False
   >>> P.closed(0, 1).adjacent(P.open(1, 2) | P.open(3, 4))
   False

   ```

 - `i.overlaps(other)` tests if there is an overlap between two intervals.
   ```python
   >>> P.closed(1, 2).overlaps(P.closed(2, 3))
   True
   >>> P.closed(1, 2).overlaps(P.open(2, 3))
   False

   ```

Finally, intervals are hashable as long as their bounds are hashable (and we have defined a hash value for `P.inf` and `-P.inf`).


[&uparrow; back to top](#table-of-contents)
### Comparison operators

Equality between intervals can be checked with the classical `==` operator:

```python
>>> P.closed(0, 2) == P.closed(0, 1) | P.closed(1, 2)
True
>>> P.closed(0, 2) == P.open(0, 2)
False

```

Moreover, intervals are comparable using `>`, `>=`, `<` or `<=`.
These comparison operators have a different behaviour than the usual ones.
For instance, `a < b` holds if all values in `a` are lower than the minimal value of `b` (i.e., `a` is entirely on the left of the lower bound of `b`).

```python
>>> P.closed(0, 1) < P.closed(2, 3)
True
>>> P.closed(0, 1) < P.closed(1, 2)
False

```

Similarly, `a <= b` if all values in `a` are lower than the maximal value of `b` (i.e., `a` is entirely on the left of the upper bound of `b`).

```python
>>> P.closed(0, 1) <= P.closed(2, 3)
True
>>> P.closed(0, 2) <= P.closed(1, 3)
True
>>> P.closed(0, 3) <= P.closed(1, 2)
False

```

If an interval needs to be compared against a single value, convert the value to a singleton interval first:

```python
>>> P.singleton(0) < P.closed(0, 10)
False
>>> P.singleton(0) <= P.closed(0, 10)
True
>>> P.singleton(5) <= P.closed(0, 10)
True
>>> P.closed(0, 1) < P.singleton(2)
True

```

Note that all these semantics differ from classical comparison operators.
As a consequence, the empty interval is never `<`, `<=`, `>` nor `>=` than any other interval, and no interval is `<`, `>`, `<=` or `>=` when compared to the empty interval.

```python
>>> e = P.empty()
>>> e < e or e > e or e <= e or e >= e
False
>>> i = P.closed(0, 1)
>>> e < i or e <= i or e > i or e >= i
False

```

Moreover, some non-empty intervals are also not comparable in the classical sense, as illustrated hereafter:

```python
>>> a, b = P.closed(0, 4), P.closed(1, 2)
>>> a < b or a > b
False
>>> a <= b or a >= b
False
>>> b <= a and b >= a
True

```

As a general rule, if `a < b` holds, then `a <= b`, `b > a`, `b >= a`, `not (a > b)`, `not (b < a)`, `not (a >= b)`, and `not (b <= a)` hold.



[&uparrow; back to top](#table-of-contents)
### Interval transformation

Intervals are immutable but provide a `replace` method to create a new interval based on the current one. This method accepts four optional parameters `left`, `lower`, `upper`, and `right`:

```python
>>> i = P.closed(0, 2)
>>> i.replace(P.OPEN, -1, 3, P.CLOSED)
(-1,3]
>>> i.replace(lower=1, right=P.OPEN)
[1,2)

```

Functions can be passed instead of values. If a function is passed, it is called with the current corresponding value.

```python
>>> P.closed(0, 2).replace(upper=lambda x: 2 * x)
[0,4]

```

The provided function won't be called on infinities, unless `ignore_inf` is set to `False`.

```python
>>> i = P.closedopen(0, P.inf)
>>> i.replace(upper=lambda x: 10)  # No change, infinity is ignored
[0,+inf)
>>> i.replace(upper=lambda x: 10, ignore_inf=False)  # Infinity is not ignored
[0,10)

```

When `replace` is applied on an interval that is not atomic, it is extended and/or restricted such that its enclosure satisfies the new bounds.

```python
>>> i = P.openclosed(0, 1) | P.closed(5, 10)
>>> i.replace(P.CLOSED, -1, 8, P.OPEN)
[-1,1] | [5,8)
>>> i.replace(lower=4)
(4,10]

```

To apply arbitrary transformations on the underlying atomic intervals, intervals expose an `apply` method that acts like `map`.
This method accepts a function that will be applied on each of the underlying atomic intervals to perform the desired transformation.
The provided function is expected to return either an `Interval`, or a 4-uple `(left, lower, upper, right)`.

```python
>>> i = P.closed(2, 3) | P.open(4, 5)
>>> # Increment bound values
>>> i.apply(lambda x: (x.left, x.lower + 1, x.upper + 1, x.right))
[3,4] | (5,6)
>>> # Invert bounds
>>> i.apply(lambda x: (~x.left, x.lower, x.upper, ~x.right))
(2,3) | [4,5]

```

The `apply` method is very powerful when used in combination with `replace`.
Because the latter allows functions to be passed as parameters and ignores infinities by default, it can be conveniently used to transform (disjunction of) intervals in presence of infinities.

```python
>>> i = P.openclosed(-P.inf, 0) | P.closed(3, 4) | P.closedopen(8, P.inf)
>>> # Increment bound values
>>> i.apply(lambda x: x.replace(upper=lambda v: v + 1))
(-inf,1] | [3,5] | [8,+inf)
>>> # Intervals are still automatically simplified
>>> i.apply(lambda x: x.replace(lower=lambda v: v * 2))
(-inf,0] | [16,+inf)
>>> # Invert bounds
>>> i.apply(lambda x: x.replace(left=lambda v: ~v, right=lambda v: ~v))
(-inf,0) | (3,4) | (8,+inf)
>>> # Replace infinities with -10 and 10
>>> conv = lambda v: -10 if v == -P.inf else (10 if v == P.inf else v)
>>> i.apply(lambda x: x.replace(lower=conv, upper=conv, ignore_inf=False))
(-10,0] | [3,4] | [8,10)

```


[&uparrow; back to top](#table-of-contents)
### Discrete iteration

The `iterate` function takes an interval, and returns a generator to iterate over the values of an interval. Obviously, as intervals are continuous, it is required to specify the  `step` between consecutive values. The iteration then starts from the lower bound and ends on the upper one. Only values contained by the interval are returned this way.

```python
>>> list(P.iterate(P.closed(0, 3), step=1))
[0, 1, 2, 3]
>>> list(P.iterate(P.closed(0, 3), step=2))
[0, 2]
>>> list(P.iterate(P.open(0, 3), step=2))
[2]

```

When an interval is not atomic, `iterate` consecutively iterates on all underlying atomic intervals, starting from each lower bound and ending on each upper one:

```python
>>> list(P.iterate(P.singleton(0) | P.singleton(3) | P.singleton(5), step=2))  # Won't be [0]
[0, 3, 5]
>>> list(P.iterate(P.closed(0, 2) | P.closed(4, 6), step=3))  # Won't be [0, 6]
[0, 4]

```

By default, the iteration always starts on the lower bound of each underlying atomic interval.
The `base` parameter can be used to change this behaviour, by specifying how the initial value to start the iteration from must be computed. This parameter accepts a callable that is called with the lower bound of each underlying atomic interval, and that returns the initial value to start the iteration from.
It can be helpful to deal with (semi-)infinite intervals, or to *align* the generated values of the iterator:

```python
>>> # Align on integers
>>> list(P.iterate(P.closed(0.3, 4.9), step=1, base=int))
[1, 2, 3, 4]
>>> # Restrict values of a (semi-)infinite interval
>>> list(P.iterate(P.openclosed(-P.inf, 2), step=1, base=lambda x: max(0, x)))
[0, 1, 2]

```

The `base` parameter can be used to change how `iterate` applies on unions of atomic interval, by specifying a function that returns a single value, as illustrated next:

```python
>>> base = lambda x: 0
>>> list(P.iterate(P.singleton(0) | P.singleton(3) | P.singleton(5), step=2, base=base))
[0]
>>> list(P.iterate(P.closed(0, 2) | P.closed(4, 6), step=3, base=base))
[0, 6]

```

Notice that defining `base` such that it returns a single value can be extremely inefficient in terms of performance when the intervals are "far apart" each other (i.e., when the *gaps* between atomic intervals are large).

Finally, iteration can be performed in reverse order by specifying `reverse=True`.

```python
>>> list(P.iterate(P.closed(0, 3), step=-1, reverse=True))  # Mind step=-1
[3, 2, 1, 0]
>>> list(P.iterate(P.closed(0, 3), step=-2, reverse=True))  # Mind step=-2
[3, 1]

```

Again, this library does not make any assumption about the objects being used in an interval, as long as they are comparable. However, it is not always possible to provide a meaningful value for `step` (e.g., what would be the step between two consecutive characters?). In these cases, a callable can be passed instead of a value.
This callable will be called with the current value, and is expected to return the next possible value.

```python
>>> list(P.iterate(P.closed('a', 'd'), step=lambda d: chr(ord(d) + 1)))
['a', 'b', 'c', 'd']
>>> # Since we reversed the order, we changed "+" to "-" in the lambda.
>>> list(P.iterate(P.closed('a', 'd'), step=lambda d: chr(ord(d) - 1), reverse=True))
['d', 'c', 'b', 'a']

```



[&uparrow; back to top](#table-of-contents)
### Map intervals to data

The library provides an `IntervalDict` class, a `dict`-like data structure to store and query data along with intervals. Any value can be stored in such data structure as long as it supports equality.


```python
>>> d = P.IntervalDict()
>>> d[P.closed(0, 3)] = 'banana'
>>> d[4] = 'apple'
>>> d
{[0,3]: 'banana', [4]: 'apple'}

```

When a value is defined for an interval that overlaps an existing one, it is automatically updated to take the new value into account:

```python
>>> d[P.closed(2, 4)] = 'orange'
>>> d
{[0,2): 'banana', [2,4]: 'orange'}

```

An `IntervalDict` can be queried using single values or intervals. If a single value is used as a key, its behaviour corresponds to the one of a classical `dict`:

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

When the key is an interval, a new `IntervalDict` containing the values for the specified key is returned:

```python
>>> d[~P.empty()]  # Get all values, similar to d.copy()
{[0,2): 'banana', [2,4]: 'orange'}
>>> d[P.closed(1, 3)]
{[1,2): 'banana', [2,3]: 'orange'}
>>> d[P.closed(-2, 1)]
{[0,1]: 'banana'}
>>> d[P.closed(-2, -1)]
{}

```

By using `.get`, a default value (defaulting to `None`) can be specified.
This value is used to "fill the gaps" if the queried interval is not completely covered by the `IntervalDict`:

```python
>>> d.get(P.closed(-2, 1), default='peach')
{[-2,0): 'peach', [0,1]: 'banana'}
>>> d.get(P.closed(-2, -1), default='peach')
{[-2,-1]: 'peach'}
>>> d.get(P.singleton(1), default='peach')  # Key is covered, default is not used
{[1]: 'banana'}

```

For convenience, an `IntervalDict` provides a way to look for specific data values.
The `.find` method always returns a (possibly empty) `Interval` instance for which given value is defined:

```python
>>> d.find('banana')
[0,2)
>>> d.find('orange')
[2,4]
>>> d.find('carrot')
()

```

The active domain of an `IntervalDict` can be retrieved with its `.domain` method.
This method always returns a single `Interval` instance, where `.keys` returns a sorted view of disjoint intervals.

```python
>>> d.domain()
[0,4]
>>> list(d.keys())
[[0,2), [2,4]]
>>> list(d.values())
['banana', 'orange']
>>> list(d.items())
[([0,2), 'banana'), ([2,4], 'orange')]

```

The `.keys`, `.values` and `.items` methods return exactly one element for each stored value (i.e., if two intervals share a value, they are merged into a disjunction), as illustrated next.
See [#44](https://github.com/AlexandreDecan/portion/issues/44#issuecomment-710199687) to know how to obtain a sorted list of atomic intervals instead.

```python
>>> d = P.IntervalDict()
>>> d[P.closed(0, 1)] = d[P.closed(2, 3)] = 'peach'
>>> list(d.items())
[([0,1] | [2,3], 'peach')]

```


Two `IntervalDict` instances can be combined using the `.combine` method.
This method returns a new `IntervalDict` whose keys and values are taken from the two source `IntervalDict`.
The values corresponding to intersecting keys (i.e., when the two instances overlap) are combined using the provided `how` function, while values corresponding to non-intersecting keys are simply copied (i.e., the `how` function is not called for them), as illustrated hereafter:

```python
>>> d1 = P.IntervalDict({P.closed(0, 2): 'banana'})
>>> d2 = P.IntervalDict({P.closed(1, 3): 'orange'})
>>> concat = lambda x, y: x + '/' + y
>>> d1.combine(d2, how=concat)
{[0,1): 'banana', [1,2]: 'banana/orange', (2,3]: 'orange'}

```

The `how` function can also receive the current interval as third parameter, by enabling the `pass_interval` parameter of `.combine`.
The `combine` method also accepts a `missing` parameter. When `missing` is set, the `how` function is called even for non-intersecting keys, using the value of `missing` to replace the missing values:

```python
>>> d1.combine(d2, how=concat, missing='kiwi')
{[0,1): 'banana/kiwi', [1,2]: 'banana/orange', (2,3]: 'kiwi/orange'}

```

Resulting keys always correspond to an outer join. Other joins can be easily simulated by querying the resulting `IntervalDict` as follows:

```python
>>> d = d1.combine(d2, how=concat)
>>> d[d1.domain()]  # Left join
{[0,1): 'banana', [1,2]: 'banana/orange'}
>>> d[d2.domain()]  # Right join
{[1,2]: 'banana/orange', (2,3]: 'orange'}
>>> d[d1.domain() & d2.domain()]  # Inner join
{[1,2]: 'banana/orange'}

```

While `.combine` accepts a single `IntervalDict`, it can be generalized to support an arbitrary number of `IntervalDicts`, as illustrated in [#95](https://github.com/AlexandreDecan/portion/issues/95#issuecomment-2351435891).

Finally, similarly to a `dict`, an `IntervalDict` also supports `len`, `in` and `del`, and defines `.clear`, `.copy`, `.update`, `.pop`, `.popitem`, and `.setdefault`.
For convenience, one can export the content of an `IntervalDict` to a classical Python `dict` using the `as_dict` method. This method accepts an optional `atomic` parameter (whose default is `False`).
When set to `True`, the keys of the resulting `dict` instance are atomic intervals.


[&uparrow; back to top](#table-of-contents)
### Import & export intervals to strings

Intervals can be exported to string, either using `repr` (as illustrated above) or with the `to_string` function.

```python
>>> P.to_string(P.closedopen(0, 1))
'[0,1)'

```

The way string representations are built can be easily parametrized using the various parameters supported by `to_string`:

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
>>> x = P.openclosed(0, 1) | P.closed(2, P.inf)
>>> P.to_string(x, **params)
'.."0" - "1"> or <"2" - +oo..'

```

Similarly, intervals can be created from a string using the `from_string` function.
A conversion function (`conv` parameter) has to be provided to convert a bound (as string) to a value.

```python
>>> P.from_string('[0, 1]', conv=int) == P.closed(0, 1)
True
>>> P.from_string('[1.2]', conv=float) == P.singleton(1.2)
True
>>> converter = lambda s: datetime.datetime.strptime(s, '%Y/%m/%d')
>>> P.from_string('[2011/03/15, 2013/10/10]', conv=converter)
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
>>> P.from_string(s, **params)
(0,1] | [2,+inf)

```

When a bound contains a comma or has a representation that cannot be automatically parsed with `from_string`, the `bound` parameter can be used to specify the regular expression that should be used to match its representation.

```python
>>> s = '[(0, 1), (2, 3)]'  # Bounds are expected to be tuples
>>> P.from_string(s, conv=eval, bound=r'\(.+?\)')
[(0, 1),(2, 3)]

```


[&uparrow; back to top](#table-of-contents)
### Import & export intervals to Python built-in data types

Intervals can also be exported to a list of 4-uples with `to_data`, e.g., to support JSON serialization.
`P.CLOSED` and `P.OPEN` are represented by Boolean values `True` (inclusive) and `False` (exclusive).

```python
>>> P.to_data(P.openclosed(0, 2))
[(False, 0, 2, True)]

```

The values used to represent positive and negative infinities can be specified with `pinf` and `ninf`. They default to `float('inf')` and `float('-inf')` respectively.

```python
>>> x = P.openclosed(0, 1) | P.closedopen(2, P.inf)
>>> P.to_data(x)
[(False, 0, 1, True), (True, 2, inf, False)]

```

The function to convert bounds can be specified with the `conv` parameter.

```python
>>> x = P.closedopen(datetime.date(2011, 3, 15), datetime.date(2013, 10, 10))
>>> P.to_data(x, conv=lambda v: (v.year, v.month, v.day))
[(True, (2011, 3, 15), (2013, 10, 10), False)]

```

Intervals can be imported from such a list of 4-tuples with `from_data`.
The same set of parameters can be used to specify how bounds and infinities are converted.

```python
>>> x = [(True, (2011, 3, 15), (2013, 10, 10), False)]
>>> P.from_data(x, conv=lambda v: datetime.date(*v))
[datetime.date(2011, 3, 15),datetime.date(2013, 10, 10))

```


[&uparrow; back to top](#table-of-contents)
### Specialize & customize intervals

**Disclaimer**: the features explained in this section are still experimental and are subject to backward incompatible changes even in minor or patch updates of `portion`.

The intervals provided by `portion` already cover a wide range of use cases.
However, in some situations, it might be interesting to specialize or customize these intervals.
One typical example would be to support discrete intervals such as intervals of integers.

While it is definitely possible to rely on the default intervals provided by `portion` to encode discrete intervals, there are a few edge cases that lead some operations to return unexpected results:

```python
>>> P.singleton(0) | P.singleton(1)  # Case 1: should be [0,1] for discrete numbers
[0] | [1]
>>> P.open(0, 1)  # Case 2: should be empty
(0,1)
>>> P.closedopen(0, 1)  # Case 3: should be singleton [0]
[0,1)

```

The `portion` library makes its best to ease defining and using subclasses of `Interval` to address these situations. In particular, `Interval` instances always produce new intervals using `self.__class__`, and the class is written in a way that most of its methods can be easily extended.

To implement a class for intervals of discrete numbers and to cover the three aforementioned cases, we need to change the behaviour of the `Interval._mergeable` class method (to address first case) and of the `Interval.from_atomic` class method (for cases 2 and 3).
The former is used to detect whether two atomic intervals can be merged into a single interval, while the latter is used to create atomic intervals.

Thankfully, since discrete intervals are expected to be a frequent use case, `portion` provides an `AbstractDiscreteInterval` class that already makes the appropriate changes to these two methods.
As indicated by its name, this class cannot be used directly and should be inherited.
In particular, one has either to provide a `_step` class attribute to define the step between consecutive discrete values, or to define the `_incr` and `_decr` class methods:

```python
>>> class IntInterval(P.AbstractDiscreteInterval):
...     _step = 1

```

That's all!
We can now use this class to manipulate intervals of discrete numbers and see it covers the three problematic cases:

```python
>>> IntInterval.from_atomic(P.CLOSED, 0, 0, P.CLOSED) | IntInterval.from_atomic(P.CLOSED, 1, 1, P.CLOSED)
[0,1]
>>> IntInterval.from_atomic(P.OPEN, 0, 1, P.OPEN)
()
>>> IntInterval.from_atomic(P.CLOSED, 0, 1, P.OPEN)
[0]

```

As an example of using `_incr` and `_decr`, consider the following `CharInterval` subclass tailored to manipulate intervals of characters:

```python
>>> class CharInterval(P.AbstractDiscreteInterval):
...     _incr = lambda v: chr(ord(v) + 1)
...     _decr = lambda v: chr(ord(v) - 1)
>>> CharInterval.from_atomic(P.OPEN, 'a', 'z', P.OPEN)
['b','y']

```

Having to call `from_atomic` on the subclass to create intervals is quite verbose.
For convenience, all the functions that create interval instances accept an additional `klass` parameter to specify the class that creates intervals, circumventing the direct use of the class constructors.
However, having to specify the `klass` parameter in each call to `P.closed` or other helpers that create intervals is still a bit too verbose to be convenient.
Consequently, `portion` provides a `create_api` function that, given a subclass of `Interval`, returns a dynamically generated module whose API is similar to the one of `portion` but configured to use the subclass instead:

```python
>>> D = P.create_api(IntInterval)
>>> D.singleton(0) | D.singleton(1)
[0,1]
>>> D.open(0, 1)
()
>>> D.closedopen(0, 1)
[0]

```

This makes it easy to use our newly defined `IntInterval` subclass while still benefiting from `portion`'s API.

Let's extend our example to support intervals of natural numbers.
Such intervals are quite similar to the above ones, except they cannot go over negative values.
We can prevent the bounds of an interval to be negative by slightly changing the `from_atomic` class method as follows:

```python
>>> class NaturalInterval(IntInterval):
...    @classmethod
...    def from_atomic(cls, left, lower, upper, right):
...        return super().from_atomic(
...            P.CLOSED if lower < 0 else left,
...            max(0, lower),
...            upper,
...            right,
...        )

```

We can now define and use the `N` module to check whether our newly defined `NaturalInterval` does the job:

```python
>>> N = P.create_api(NaturalInterval)
>>> N.closed(-10, 2)
[0,2]
>>> N.open(-10, 2)
[0,1]
>>> ~N.empty()
[0,+inf)

```

Keep in mind that just because `NaturalInterval` has semantics associated with natural numbers does not mean that all possible operations on these intervals strictly comply the semantics.
The following examples illustrate some of the cases where additional checks should be implemented to strictly adhere to these semantics:

```python
>>> N.closed(1.5, 2.5)  # Bounds are not natural numbers
[1.5,2.5]
>>> 0.5 in N.closed(0, 1)  # Given value is not a natural number
True
>>> ~N.singleton(0.5)
[1.5,+inf)

```



[&uparrow; back to top](#table-of-contents)
## Changelog

This library adheres to a [semantic versioning](https://semver.org) scheme.
See [CHANGELOG.md](https://github.com/AlexandreDecan/portion/blob/master/CHANGELOG.md) for the list of changes.



## Contributions

Contributions are very welcome!
Feel free to report bugs or suggest new features using GitHub issues and/or pull requests.



## License

Distributed under [LGPLv3 - GNU Lesser General Public License, version 3](https://github.com/AlexandreDecan/portion/blob/master/LICENSE.txt).

You can refer to this library using:

```
@software{portion,
  author = {Decan, Alexandre},
  title = {portion: Python data structure and operations for intervals},
  url = {https://github.com/AlexandreDecan/portion},
}
```


