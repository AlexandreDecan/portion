import re

__package__ = 'python-intervals'
__version__ = '1.5.4'
__licence__ = 'LGPL3'
__author__ = 'Alexandre Decan'
__url__ = 'https://github.com/AlexandreDecan/python-intervals'
__description__ = 'Interval arithmetic for Python'


__all__ = [
    'inf', 'CLOSED', 'OPEN',
    'Interval',  # 'AtomicInterval',
    'open', 'closed', 'openclosed', 'closedopen', 'singleton', 'empty',
    'from_string', 'to_string',
]


class _PInf:
    """
    Represent positive infinity.
    """

    def __neg__(self): return _NInf()

    def __lt__(self, o): return False

    def __le__(self, o): return isinstance(o, _PInf)

    def __gt__(self, o): return not isinstance(o, _PInf)

    def __ge__(self, o): return True

    def __eq__(self, o): return isinstance(o, _PInf)

    def __ne__(self, o): return not self == o  # Required for Python 2

    def __repr__(self): return '+inf'


class _NInf:
    """
    Represent negative infinity.
    """

    def __neg__(self): return _PInf()

    def __lt__(self, o): return not isinstance(o, _NInf)

    def __le__(self, o): return True

    def __gt__(self, o): return False

    def __ge__(self, o): return isinstance(o, _NInf)

    def __eq__(self, o): return isinstance(o, _NInf)

    def __ne__(self, o): return not self == o  # Required for Python 2

    def __repr__(self): return '-inf'


# Positive infinity
inf = _PInf()

# Boundary types (True for inclusive, False for exclusive)
CLOSED = True
OPEN = False


def open(lower, upper):
    """
    Create an open interval with given bounds.
    """
    return Interval(AtomicInterval(OPEN, lower, upper, OPEN))


def closed(lower, upper):
    """
    Create a closed interval with given bounds.
    """
    return Interval(AtomicInterval(CLOSED, lower, upper, CLOSED))


def openclosed(lower, upper):
    """
    Create an left-open interval with given bounds.
    """
    return Interval(AtomicInterval(OPEN, lower, upper, CLOSED))


def closedopen(lower, upper):
    """
    Create an right-open interval with given bounds.
    """
    return Interval(AtomicInterval(CLOSED, lower, upper, OPEN))


def singleton(value):
    """
    Create a singleton.
    """
    return Interval(AtomicInterval(CLOSED, value, value, CLOSED))


def empty():
    """
    Create an empty set.
    """
    return Interval(AtomicInterval(OPEN, inf, -inf, OPEN))


def from_string(string, conv, bound=r'.+?', disj=r' ?\| ?', sep=r', ?', left_open=r'\(', left_closed=r'\[', right_open=r'\)', right_closed=r'\]'):
    """
    Parse given string and create an Interval instance.
    A converter function has to be provided to convert a bound (as string) to a value.

    :param string: string to parse.
    :param conv: function that converts a bound (as string) to an object.
    :param bound: regular expression that matches a value.
    :param disj: regular expression that matches the disjunctive operator (default matches '|').
    :param sep: regular expression that matches bound separator (default matches ',').
    :param left_open: regular expression that matches a left open boundary (default matches '(').
    :param left_closed: regular expression that matches a left closed boundary (default matches '[').
    :param right_open: regular expression that matches a right open boundary (default matches ')').
    :param right_closed: regular expression that matches a right closed boundary (default matches ']').
    :return: an Interval instance.
    """

    re_left_boundary = r'(?P<left>{}|{})'.format(left_open, left_closed)
    re_right_boundary = r'(?P<right>{}|{})'.format(right_open, right_closed)
    re_bounds = r'(?P<lower>{bound})({sep}(?P<upper>{bound}))?'.format(bound=bound, sep=sep)
    re_interval = r'{}(|{}){}'.format(re_left_boundary, re_bounds, re_right_boundary)
    re_intervals = r'{}(?P<disj>{})?'.format(re_interval, disj)

    intervals = []
    has_more = True

    while has_more:
        match = re.match(re_intervals, string)
        if match is None:
            has_more = False
        else:
            group = match.groupdict()

            left = re.match(left_closed + '$', group['left']) is not None
            right = re.match(right_closed + '$', group['right']) is not None

            lower = group.get('lower', None)
            upper = group.get('upper', None)
            lower = conv(lower) if lower is not None else inf
            upper = conv(upper) if upper is not None else lower

            intervals.append(AtomicInterval(left, lower, upper, right))
            string = string[match.end():]

    return Interval(*intervals)


def to_string(interval, conv=repr, disj=' | ', sep=',', left_open='(', left_closed='[', right_open=')', right_closed=']'):
    """
    Export given interval (or atomic interval) to string.

    :param interval: an Interval or AtomicInterval instance.
    :param conv: function that is used to represent a bound (default is `repr`).
    :param disj: string representing disjunctive operator (default is ' | ').
    :param sep: string representing bound separator (default is ',').
    :param left_open: string representing left open boundary (default is '(').
    :param left_closed: string representing left closed boundary (default is '[').
    :param right_open: string representing right open boundary (default is ')').
    :param right_closed: string representing right closed boundary (default is ']').
    :return: a string representation for given interval.
    """
    interval = Interval(interval) if isinstance(interval, AtomicInterval) else interval

    if interval.is_empty():
        return '{}{}'.format(left_open, right_open)

    exported_intervals = []
    for item in interval:
        left = left_open if item.left == OPEN else left_closed
        right = right_open if item.right == OPEN else right_closed

        lower = conv(item.lower)
        upper = conv(item.upper)

        if item.lower == item.upper:
            exported_intervals.append('{}{}{}'.format(left, lower, right))
        else:
            exported_intervals.append('{}{}{}{}{}'.format(left, lower, sep, upper, right))

    return disj.join(exported_intervals)


class AtomicInterval:
    """
    This class represents an atomic interval.

    An atomic interval is a single interval, with a lower and upper bounds, and two (closed or open) boundaries.
    """

    __slots__ = ('_left', '_lower', '_upper', '_right')

    def __init__(self, left, lower, upper, right):
        """
        Create an atomic interval.

        If a bound is set to infinity (regardless of its sign), the corresponding boundary will be exclusive.

        :param left: Boolean indicating whether the left boundary is inclusive (True) or exclusive (False).
        :param lower: lower bound value.
        :param upper: upper bound value.
        :param right: Boolean indicating whether the right boundary is inclusive (True) or exclusive (False).
        """
        self._left = left if lower not in [inf, -inf] else OPEN
        self._lower = lower
        self._upper = upper
        self._right = right if upper not in [inf, -inf] else OPEN

        if self.is_empty():
            self._left = OPEN
            self._lower = inf
            self._upper = -inf
            self._right = OPEN

    @property
    def left(self):
        """
        Boolean indicating whether the left boundary is inclusive (True) or exclusive (False).
        """
        return self._left

    @property
    def lower(self):
        """
        Lower bound value.
        """
        return self._lower

    @property
    def upper(self):
        """
        Upper bound value.
        """
        return self._upper

    @property
    def right(self):
        """
        Boolean indicating whether the right boundary is inclusive (True) or exclusive (False).
        """
        return self._right

    def is_empty(self):
        """
        Test interval emptiness.

        :return: True if interval is empty, False otherwise.
        """
        return (
            self._lower > self._upper or
            (self._lower == self._upper and (self._left == OPEN or self._right == OPEN))
        )

    def overlaps(self, other, permissive=False):
        """
        Test if intervals have any overlapping value.

        If 'permissive' is set to True (default is False), then [1, 2) and [2, 3] are considered as having
        an overlap on value 2 (but not [1, 2) and (2, 3]).

        :param other: an atomic interval.
        :param permissive: set to True to consider contiguous intervals as well.
        :return True if intervals overlap, False otherwise.
        """
        if not isinstance(other, AtomicInterval):
            raise TypeError('Only AtomicInterval instances are supported.')

        if self._lower > other.lower:
            first, second = other, self
        else:
            first, second = self, other

        if first._upper == second._lower:
            if permissive:
                return first._right == CLOSED or second._left == CLOSED
            else:
                return first._right == CLOSED and second._left == CLOSED

        return first._upper > second._lower

    def intersection(self, other):
        """
        Return the intersection of two intervals.

        :param other: an interval.
        :return: the intersection of the intervals.
        """
        return self & other

    def union(self, other):
        """
        Return the union of two intervals. If the union cannot be represented using a single atomic interval,
        return an Interval instance (which corresponds to an union of atomic intervals).

        :param other: an interval.
        :return: the union of the intervals.
        """
        return self | other

    def contains(self, item):
        """
        Test if given item is contained in this interval.
        This method accepts atomic intervals, intervals and arbitrary values.

        :param item: an atomic interval, an interval or any arbitrary value.
        :return: True if given item is contained, False otherwise.
        """
        return item in self

    def complement(self):
        """
        Return the complement of this interval.

        Complementing an interval always results in an Interval instance, even if the complement
        can be encoded as a single atomic interval.

        :return: the complement of this interval.
        """
        return ~self

    def difference(self, other):
        """
        Return the difference of two intervals.

        :param other: an interval.
        :return: the difference of the intervals.
        """
        return self - other

    def __and__(self, other):
        if isinstance(other, AtomicInterval):
            if self._lower == other._lower:
                lower = self._lower
                left = self._left if self._left == OPEN else other._left
            else:
                lower = max(self._lower, other._lower)
                left = self._left if lower == self._lower else other._left

            if self._upper == other._upper:
                upper = self._upper
                right = self._right if self._right == OPEN else other._right
            else:
                upper = min(self._upper, other._upper)
                right = self._right if upper == self._upper else other._right

            if lower <= upper:
                return AtomicInterval(left, lower, upper, right)
            else:
                return AtomicInterval(OPEN, lower, lower, OPEN)
        else:
            return NotImplemented

    def __or__(self, other):
        if isinstance(other, AtomicInterval):
            if self.overlaps(other, permissive=True):
                if self._lower == other._lower:
                    lower = self._lower
                    left = self._left if self._left == OPEN else other._left
                else:
                    lower = min(self._lower, other._lower)
                    left = self._left if lower == self._lower else other._left

                if self._upper == other._upper:
                    upper = self._upper
                    right = self._right if self._right == OPEN else other._right
                else:
                    upper = max(self._upper, other._upper)
                    right = self._right if upper == self._upper else other._right

                return AtomicInterval(left, lower, upper, right)
            else:
                return Interval(self, other)
        else:
            return NotImplemented

    def __contains__(self, item):
        if isinstance(item, AtomicInterval):
            left = item._lower > self._lower or (
                    item._lower == self._lower and (item._left == self._left or self._left == CLOSED))
            right = item._upper < self._upper or (
                    item._upper == self._upper and (item._right == self._right or self._right == CLOSED))
            return left and right
        elif isinstance(item, Interval):
            for interval in item:
                if interval not in self:
                    return False
            return True
        else:
            left = (item >= self._lower) if self._left == CLOSED else (item > self._lower)
            right = (item <= self._upper) if self._right == CLOSED else (item < self._upper)
            return left and right

    def __invert__(self):
        inverted_left = OPEN if self._left == CLOSED else CLOSED
        inverted_right = OPEN if self._right == CLOSED else CLOSED

        return Interval(
            AtomicInterval(OPEN, -inf, self._lower, inverted_left),
            AtomicInterval(inverted_right, self._upper, inf, OPEN)
        )

    def __sub__(self, other):
        if isinstance(other, AtomicInterval):
            return self & ~other
        else:
            return NotImplemented

    def __eq__(self, other):
        if isinstance(other, AtomicInterval):
            return (
                    self._left == other._left and
                    self._lower == other._lower and
                    self._upper == other._upper and
                    self._right == other._right
            )
        else:
            return NotImplemented

    def __ne__(self, other):
        return not self == other  # Required for Python 2

    def __lt__(self, other):
        if isinstance(other, Interval):
            other = other.to_atomic()

        if isinstance(other, AtomicInterval):
            if self._right == OPEN:
                return self._upper <= other._lower
            else:
                return self._upper < other._lower or (self._upper == other._lower and other._left == OPEN)
        else:
            return NotImplemented

    def __gt__(self, other):
        if isinstance(other, Interval):
            other = other.to_atomic()

        if isinstance(other, AtomicInterval):
            if self._left == OPEN:
                return self._lower >= other._upper
            else:
                return self._lower > other._upper or (self._lower == other._upper and other._right == OPEN)
        else:
            return NotImplemented

    def __le__(self, other):
        if isinstance(other, Interval):
            other = other.to_atomic()

        if isinstance(other, AtomicInterval):
            if self._right == OPEN:
                return self._upper <= other._upper
            else:
                return self._upper < other._upper or (self._upper == other._upper and other._right == CLOSED)
        else:
            return NotImplemented

    def __ge__(self, other):
        if isinstance(other, Interval):
            other = other.to_atomic()

        if isinstance(other, AtomicInterval):
            if self._left == OPEN:
                return self._lower >= other._lower
            else:
                return self._lower > other._lower or (self._lower == other._lower and other._left == CLOSED)
        else:
            return NotImplemented

    def __hash__(self):
        try:
            return hash(self._lower)
        except TypeError:
            return 0

    def __repr__(self):
        if self.is_empty():
            return '()'
        elif self._lower == self._upper:
            return '[{}]'.format(repr(self._lower))
        else:
            return '{}{},{}{}'.format(
                '[' if self._left == CLOSED else '(',
                repr(self._lower),
                repr(self._upper),
                ']' if self._right == CLOSED else ')',
            )


class Interval:
    """
    This class represents an interval.

    An interval is an (automatically simplified) union of atomic intervals.
    It can be created either by passing (atomic) intervals, or by using one of the helpers
    provided in this module (open(..), closed(..), etc).

    Unless explicitly specified, all operations on an Interval instance return Interval instances.
    """

    __slots__ = ('_intervals',)

    def __init__(self, *intervals):
        """
        Create an interval from a list of (atomic or not) intervals.

        :param intervals: a list of (atomic or not) intervals.
        """
        self._intervals = list()

        for interval in intervals:
            if isinstance(interval, Interval):
                self._intervals.extend(interval)
            elif isinstance(interval, AtomicInterval):
                if not interval.is_empty():
                    self._intervals.append(interval)
            else:
                raise TypeError('Parameters must be Interval or AtomicInterval instances')

        if len(self._intervals) == 0:
            # So we have at least one (empty) interval
            self._intervals.append(AtomicInterval(OPEN, inf, -inf, OPEN))
        else:
            # Sort intervals by lower bound
            self._intervals.sort(key=lambda i: i.lower)

            i = 0
            # Attempt to merge consecutive intervals
            while i < len(self._intervals) - 1:
                current = self._intervals[i]
                successor = self._intervals[i + 1]

                if current.overlaps(successor, permissive=True):
                    interval = current | successor
                    self._intervals.pop(i)
                    self._intervals.pop(i)
                    self._intervals.insert(i, interval)
                else:
                    i = i + 1

    def is_empty(self):
        """
        Test interval emptiness.

        :return: True iff interval is empty.
        """
        return self.is_atomic() and self._intervals[0].is_empty()

    def is_atomic(self):
        """
        Test interval atomicity. An interval is atomic if it is composed of a single atomic interval.

        :return: True if this interval is atomic, False otherwise.
        """
        return len(self._intervals) == 1

    def to_atomic(self):
        """
        Return the smallest atomic interval containing this interval.

        :return: an AtomicInterval instance.
        """
        lower = self._intervals[0].lower
        left = self._intervals[0].left
        upper = self._intervals[-1].upper
        right = self._intervals[-1].right

        return AtomicInterval(left, lower, upper, right)

    def enclosure(self):
        """
        Return the smallest interval composed of a single atomic interval that encloses the current interval.
        Is equivalent to Interval(self.to_atomic())

        :return: an Interval instance.
        """
        return Interval(self.to_atomic())

    def overlaps(self, other, permissive=False):
        """
        Test if intervals have any overlapping value.

        If 'permissive' is set to True (default is False), then [1, 2) and [2, 3] are considered as having
        an overlap on value 2 (but not [1, 2) and (2, 3]).

        :param other: an interval or atomic interval.
        :param permissive: set to True to consider contiguous intervals as well.
        :return True if intervals overlap, False otherwise.
        """
        if isinstance(other, AtomicInterval):
            for interval in self._intervals:
                if interval.overlaps(other, permissive=permissive):
                    return True
            return False
        elif isinstance(other, Interval):
            for o_interval in other._intervals:
                if self.overlaps(o_interval, permissive=permissive):
                    return True
            return False
        else:
            raise TypeError('Unsupported type {} for {}'.format(type(other), other))

    def intersection(self, other):
        """
        Return the intersection of two intervals.

        :param other: an interval or atomic interval.
        :return: the intersection of the intervals.
        """
        return self & other

    def union(self, other):
        """
        Return the union of two intervals.

        :param other: an interval or atomic interval.
        :return: the union of the intervals.
        """
        return self | other

    def contains(self, item):
        """
        Test if given item is contained in this interval.
        This method accepts atomic intervals, intervals and arbitrary values.

        :param item: an atomic interval, an interval or any arbitrary value.
        :return: True if given item is contained, False otherwise.
        """
        return item in self

    def complement(self):
        """
        Return the complement of this interval.

        :return: the complement of this interval.
        """
        return ~self

    def difference(self, other):
        """
        Return the difference of two intervals.

        :param other: an interval or an atomic interval.
        :return: the difference of the intervals.
        """
        return self - other

    def __len__(self):
        if self._intervals[0].is_empty():
            return 0
        else:
            return len(self._intervals)

    def __iter__(self):
        if self._intervals[0].is_empty():
            return iter([])
        else:
            return iter(self._intervals)

    def __getitem__(self, item):
        if self._intervals[0].is_empty():
            raise IndexError('Interval is empty')
        else:
            return self._intervals[item]

    def __and__(self, other):
        if isinstance(other, (AtomicInterval, Interval)):
            if isinstance(other, AtomicInterval):
                intervals = [other]
            else:
                intervals = list(other._intervals)
            new_intervals = []
            for interval in self._intervals:
                for o_interval in intervals:
                    new_intervals.append(interval & o_interval)
            return Interval(*new_intervals)
        else:
            return NotImplemented

    def __rand__(self, other):
        return self & other

    def __or__(self, other):
        if isinstance(other, AtomicInterval):
            return self | Interval(other)
        elif isinstance(other, Interval):
            return Interval(*(list(self._intervals) + list(other._intervals)))
        else:
            return NotImplemented

    def __ror__(self, other):
        return self | other

    def __contains__(self, item):
        if isinstance(item, Interval):
            for o_interval in item._intervals:
                if o_interval not in self:
                    return False
            return True
        elif isinstance(item, AtomicInterval):
            for interval in self._intervals:
                if item in interval:
                    return True
            return False
        else:
            for interval in self._intervals:
                if item in interval:
                    return True
            return False

    def __invert__(self):
        complements = [~i for i in self._intervals]
        intersection = complements[0]
        for interval in complements:
            intersection = intersection & interval
        return intersection

    def __sub__(self, other):
        if isinstance(other, (AtomicInterval, Interval)):
            return self & ~other
        else:
            return NotImplemented

    def __rsub__(self, other):
        return other & ~self

    def __eq__(self, other):
        if isinstance(other, AtomicInterval):
            return Interval(other) == self
        elif isinstance(other, Interval):
            return self._intervals == other._intervals
        else:
            return NotImplemented

    def __ne__(self, other):
        return not self == other  # Required for Python 2

    def __lt__(self, other):
        if isinstance(other, AtomicInterval):
            return self._intervals[-1] < other
        elif isinstance(other, Interval):
            return self._intervals[-1] < other._intervals[0]
        else:
            return NotImplemented

    def __gt__(self, other):
        if isinstance(other, AtomicInterval):
            return self._intervals[0] > other
        elif isinstance(other, Interval):
            return self._intervals[0] > other._intervals[-1]
        else:
            return NotImplemented

    def __le__(self, other):
        if isinstance(other, AtomicInterval):
            return self._intervals[-1] <= other
        elif isinstance(other, Interval):
            return self._intervals[-1] <= other._intervals[-1]
        else:
            return NotImplemented

    def __ge__(self, other):
        if isinstance(other, AtomicInterval):
            return self._intervals[0] >= other
        elif isinstance(other, Interval):
            return self._intervals[0] >= other._intervals[0]
        else:
            return NotImplemented

    def __hash__(self):
        return hash(self._intervals[0])

    def __repr__(self):
        return ' | '.join(repr(i) for i in self._intervals)
