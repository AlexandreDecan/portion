__name__ = 'python-intervals'
__version__ = '1.2.0'
__author__ = 'Alexandre Decan'
__author_email__ = 'alexandre.decan@lexpage.net'
__licence__ = 'LGPL3'
__description__ = 'Python Intervals Arithmetic'
__url__ = 'https://github.com/AlexandreDecan/python-intervals'


__ALL__ = [
    'inf', 'CLOSED', 'OPEN',
    'Interval', 'AtomicInterval',
    'open', 'closed', 'openclosed', 'closedopen', 'singleton'
]


class _PInf:
    """
    Use to represent positive infinity.
    """

    def __neg__(self): return _NInf()

    def __lt__(self, o): return False

    def __le__(self, o): return isinstance(o, _PInf)

    def __gt__(self, o): return not isinstance(o, _PInf)

    def __ge__(self, o): return True

    def __eq__(self, o): return isinstance(o, _PInf)

    def __repr__(self):  return '+inf'


class _NInf:
    """
    Use to represent negative infinity.
    """

    def __neg__(self): return _PInf()

    def __lt__(self, o): return not isinstance(o, _NInf)

    def __le__(self, o): return True

    def __gt__(self, o): return False

    def __ge__(self, o): return isinstance(o, _NInf)

    def __eq__(self, o): return isinstance(o, _NInf)

    def __repr__(self):  return '-inf'


inf = _PInf()

OPEN = False
CLOSED = True


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
    Create a singleton
    """
    return Interval(AtomicInterval(CLOSED, value, value, CLOSED))


def empty():
    """
    Create an empty set
    """
    return Interval(AtomicInterval(OPEN, inf, inf, OPEN))


class AtomicInterval:
    """
    Represent an (open/closed) interval.
    """

    def __init__(self, left, lower, upper, right):
        if lower > upper:
            raise ValueError(
                'Bounds are not ordered correctly: lower bound {} must be smaller than upper bound {}'.format(lower, upper))

        self._left = left if lower != -inf else OPEN
        self._lower = lower
        self._upper = upper
        self._right = right if upper != inf else OPEN

    @property
    def left(self):
        """
        Left boundary, either CLOSED or OPEN.
        """
        return self._left

    @property
    def lower(self):
        """
        Lower bound.
        """
        return self._lower

    @property
    def upper(self):
        """
        Upper bound.
        """
        return self._upper

    @property
    def right(self):
        """
        Right boundary, either CLOSED or OPEN.
        """
        return self._right

    def is_empty(self):
        """
        :return: True if interval is empty
        """
        return self._lower == self._upper and (self._left == OPEN or self._right == OPEN)

    def overlaps(self, other, permissive=False):
        """
        Return True if sets have any overlapping value.

        If 'permissive' is set to True, it considers [1, 2) and [2, 3] as an
        overlap on value 2, not [1, 2) and (2, 3].

        Only supports AtomicInterval.
        """
        if not isinstance(other, AtomicInterval):
            raise TypeError('Only AtomicInterval instances are supported.')

        if self._lower > other.lower:
            first, second = other, self
        else:
            first, second = self, other

        if first._upper == second._lower:
            if permissive:
                return first._right == CLOSED or second._right == CLOSED
            else:
                return first._right == CLOSED and second._right == CLOSED

        return first._upper > second._lower

    def intersection(self, other):
        return self & other

    def union(self, other):
        return self | other

    def contains(self, item):
        return item in self

    def complement(self):
        return ~self

    def difference(self, other):
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
        elif isinstance(other, Interval):
            return other & self
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
        elif isinstance(other, Interval):
            return other | self
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

    def __lt__(self, other):
        if isinstance(other, AtomicInterval):
            return self._upper <= other._lower and not self.overlaps(other)
        else:
            return NotImplemented

    def __gt__(self, other):
        if isinstance(other, AtomicInterval):
            return self._lower >= other._upper and not self.overlaps(other)
        else:
            return NotImplemented

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other

    def __hash__(self):
        try:
            return hash(self._lower)
        except TypeError:
            return 0

    def __repr__(self):
        if self.is_empty():
            return '()'
        elif self._lower == self._upper:
            return '[{}]'.format(self._lower)
        else:
            return '{}{},{}{}'.format(
                '[' if self._left == CLOSED else '(',
                repr(self._lower),
                repr(self._upper),
                ']' if self._right == CLOSED else ')',
            )


class Interval:
    """
    Represent an interval (union of atomic intervals).
    Can be instanciated by providing AtomicIntervals, but consider using one of the helpers
    to create Interval objects (open, closed, openclosed, closedopen, singleton, or empty).
    """

    def __init__(self, *intervals):
        self._intervals = list()

        for interval in intervals:
            if not interval.is_empty():
                self._intervals.append(interval)

        if len(self._intervals) == 0:
            # So we have at least one (empty) interval
            self._intervals.append(AtomicInterval(OPEN, inf, inf, OPEN))
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
        :return: True if interval is empty.
        """
        return self.is_atomic() and self._intervals[0].is_empty()

    def is_atomic(self):
        """
        :return: True if interval is atomic (ie. union of a single (possibly empty) atomic interval).
        """
        return len(self._intervals) == 1

    def to_atomic(self):
        """
        Return an AtomicInterval instance that contains this Interval.
        :return: An AtomicInterval instance that contains this Interval.
        """
        lower = self._intervals[0].lower
        left = self._intervals[0].left
        upper = self._intervals[-1].upper
        right = self._intervals[-1].right

        return AtomicInterval(left, lower, upper, right)

    def enclosure(self):
        """
        :return: Smallest interval that include the current one.
        """
        return Interval(self.to_atomic())

    def overlaps(self, other, permissive=False):
        """
        Return True if intervals have any overlapping value.
        If 'permissive' is set to True, it considers [1, 2) and [2, 3] as an
        overlap on value 2, not [1, 2) and (2, 3].
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
        :param other: Other Interval or AtomicInterval
        :return: Intersection between the two intervals
        """
        return self & other

    def union(self, other):
        """
        :param other: Other Interval or AtomicInterval
        :return: Union of given intervals
        """
        return self | other

    def contains(self, item):
        """
        Return True if given item is contained in this interval.
        Item must be either a value, an AtomicInterval or an Interval.
        :param item: a value, an AtomicInterval or an Interval
        :return: True if given item is contained in this interval.
        """
        return item in self

    def complement(self):
        """
        :return: The complement for this interval.
        """
        return ~self

    def difference(self, other):
        """
        :param other: Other Interval or AtomicInterval
        :return: Difference betwen given intervals.
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

    def __or__(self, other):
        if isinstance(other, AtomicInterval):
            return self | Interval(other)
        elif isinstance(other, Interval):
            return Interval(*(list(self._intervals) + list(other._intervals)))
        else:
            return NotImplemented

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

    def __eq__(self, other):
        if isinstance(other, AtomicInterval):
            return Interval(other) == self
        elif isinstance(other, Interval):
            return self._intervals == other._intervals
        else:
            return NotImplemented

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
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other

    def __hash__(self):
        return hash(self._intervals[0])

    def __repr__(self):
        return ' | '.join(repr(i) for i in self._intervals)
