from itertools import combinations
import operator


__name__ = 'python-intervals'
__version__ = '1.0.2'
__author__ = 'Alexandre Decan'
__author_email__ = 'alexandre.decan@lexpage.net'
__licence__ = 'LGPL3'
__description__ = 'Python Intervals Arithmetic'
__url__ = 'https://github.com/AlexandreDecan/python-intervals'


__ALL__ = ['inf', 'CLOSED', 'OPEN', 'Interval', 'AtomicInterval', 'open', 'closed', 'openclosed', 'closedopen']


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
        """
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
            raise ValueError('Unsupported type {} for {}'.format(type(other), other))

    def union(self, other):
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
            raise ValueError('Unsupported type {} for {}'.format(type(other), other))

    def contains(self, item):
        """
        Return True if given item is contained in this atomic interval.
        Item must be either a value, an AtomicInterval or an Interval.
        :param item: a value, an AtomicInterval or an Interval
        :return: True if given item is contained in this atomic interval.
        """
        if isinstance(item, AtomicInterval):
            left = item._lower > self._lower or (
                    item._lower == self._lower and (item._left == self._left or self._left == CLOSED))
            right = item._upper < self._upper or (
                    item._upper == self._upper and (item._right == self._right or self._right == CLOSED))
            return left and right
        else:
            left = (item >= self._lower) if self._left == CLOSED else (item > self._lower)
            right = (item <= self._upper) if self._right == CLOSED else (item < self._upper)
            return left and right

    def complement(self):
        inverted_left = OPEN if self._left == CLOSED else CLOSED
        inverted_right = OPEN if self._right == CLOSED else CLOSED
        return Interval(
            AtomicInterval(OPEN, -inf, self._lower, inverted_left),
            AtomicInterval(inverted_right, self._upper, inf, OPEN)
        )

    def difference(self, other):
        if isinstance(other, AtomicInterval):
            return self & ~other
        else:
            raise ValueError('Unsupported type {} for {}'.format(type(other), other))

    def __and__(self, other):
        try:
            return self.intersection(other)
        except ValueError:
            return NotImplemented

    def __or__(self, other):
        try:
            return self.union(other)
        except ValueError:
            return NotImplemented

    def __contains__(self, item):
        return self.contains(item)

    def __invert__(self):
        return self.complement()

    def __sub__(self, other):
        try:
            return self.difference(other)
        except ValueError:
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

    def __hash__(self):
        try:
            return hash(self._lower)
        except TypeError:
            return 0

    def __repr__(self):
        if self.is_empty():
            return '()'

        return '{}{},{}{}'.format(
            '[' if self._left == CLOSED else '(',
            repr(self._lower),
            repr(self._upper),
            ']' if self._right == CLOSED else ')',
        )


class Interval:
    """
    Represent an interval (union of atomic intervals).
    Consider using open, closed, openclosed or closedopen to create an Interval.
    """

    def __init__(self, interval, *intervals):
        self._intervals = set()

        self._intervals.add(interval)
        for interval in intervals:
            self._intervals.add(interval)

        self._clean()

    def _clean(self):
        # Remove empty intervals
        self._intervals = {i for i in self._intervals if not i.is_empty()}

        # Remove intervals contained in other ones
        to_remove = set()
        for i1, i2 in combinations(self._intervals, 2):
            if i1 not in to_remove and i1 in i2:
                to_remove.add(i1)
        self._intervals = self._intervals.difference(to_remove)

        # Merge contiguous intervals
        to_remove = set()
        to_add = set()
        for i1, i2 in combinations(self._intervals, 2):
            if i1 not in to_remove and i2 not in to_remove and i1.overlaps(i2, permissive=True):
                # Merge i1 and i2
                i3 = i1 | i2
                assert isinstance(i3, AtomicInterval)
                to_remove.add(i1)
                to_remove.add(i2)
                to_add.add(i3)

        # Do until nothing change
        self._intervals = self._intervals.difference(to_remove).union(to_add)
        if len(to_remove) + len(to_add) > 0:
            self._clean()

        # If there is no remaining interval, set the empty one
        if len(self._intervals) == 0:
            self._intervals.add(AtomicInterval(OPEN, inf, inf, OPEN))

    def is_empty(self):
        """
        :return: True if interval is empty.
        """
        return self.is_atomic() and next(iter(self._intervals)).is_empty()

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
        first = next(iter(self._intervals))

        lower = first.lower
        left = first.left
        upper = first.upper
        right = first.right

        for interval in self._intervals:
            if interval.lower < lower:
                lower = interval.lower
                left = interval.left
            elif interval.lower == lower:
                if left == OPEN and interval.left == CLOSED:
                    left = CLOSED

            if interval.upper > upper:
                upper = interval.upper
                right = interval.right
            elif interval.upper == upper:
                if right == OPEN and interval.right == CLOSED:
                    right = CLOSED

        return AtomicInterval(left, lower, upper, right)

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
            raise ValueError('Unsupported type {} for {}'.format(type(other), other))

    def intersection(self, other):
        """
        :param other: Other Interval or AtomicInterval
        :return: Intersection between the two intervals
        """
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
            raise ValueError('Unsupported type {} for {}'.format(type(other), other))

    def union(self, other):
        """
        :param other: Other Interval or AtomicInterval
        :return: Union of given intervals
        """
        if isinstance(other, AtomicInterval):
            return self | Interval(other)
        elif isinstance(other, Interval):
            return Interval(*(list(self._intervals) + list(other._intervals)))
        else:
            raise ValueError('Unsupported type {} for {}'.format(type(other), other))

    def contains(self, item):
        """
        Return True if given item is contained in this interval.
        Item must be either a value, an AtomicInterval or an Interval.
        :param item: a value, an AtomicInterval or an Interval
        :return: True if given item is contained in this interval.
        """
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

    def complement(self):
        """
        :return: The complement for this interval.
        """
        complements = map(operator.invert, self._intervals)
        intersection = next(iter(complements))
        for interval in complements:
            intersection = intersection & interval
        return intersection

    def difference(self, other):
        """
        :param other: Other Interval or AtomicInterval
        :return: Difference betwen given intervals.
        """
        if isinstance(other, (AtomicInterval, Interval)):
            return self & ~other
        else:
            raise ValueError('Unsupported type {} for {}'.format(type(other), other))

    def __len__(self):
        return len([i for i in self._intervals if not i.is_empty()])

    def __iter__(self):
        return iter(
            sorted(
                [i for i in self._intervals if not i.is_empty()]
                , key=lambda i: i.lower
            )
        )

    def __and__(self, other):
        try:
            return self.intersection(other)
        except ValueError:
            return NotImplemented

    def __or__(self, other):
        try:
            return self.union(other)
        except ValueError:
            return NotImplemented

    def __contains__(self, item):
        return self.contains(item)

    def __invert__(self):
        return self.complement()

    def __sub__(self, other):
        try:
            return self.difference(other)
        except ValueError:
            return NotImplemented

    def __eq__(self, other):
        if isinstance(other, AtomicInterval):
            return Interval(other) == self
        elif isinstance(other, Interval):
            return self._intervals == other._intervals
        else:
            return NotImplemented

    def __hash__(self):
        return hash(next(iter(self._intervals)))

    def __repr__(self):
        return ' | '.join(repr(i) for i in self._intervals)
