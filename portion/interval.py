from collections import namedtuple
from .const import Bound, inf


Atomic = namedtuple('Atomic', ['left', 'lower', 'upper', 'right'])


def mergeable(a, b):
    """
    Tester whether two atomic intervals can be merged (i.e. they overlap or are adjacent).

    :param a: an atomic interval.
    :param b: an atomic interval.
    :return: True if mergeable, False otherwise.
    """
    if a.lower < b.lower or (a.lower == b.lower and a.left == Bound.CLOSED):
        first, second = a, b
    else:
        first, second = b, a

    if first.upper == second.lower:
        return first.right == Bound.CLOSED or second.left == Bound.CLOSED

    return first.upper > second.lower


def open(lower, upper):
    """
    Create an open interval with given bounds.

    :param lower: value of the lower bound.
    :param upper: value of the upper bound.
    :return: an interval.
    """
    return Interval.from_atomic(Bound.OPEN, lower, upper, Bound.OPEN)


def closed(lower, upper):
    """
    Create a closed interval with given bounds.

    :param lower: value of the lower bound.
    :param upper: value of the upper bound.
    :return: an interval.
    """
    return Interval.from_atomic(Bound.CLOSED, lower, upper, Bound.CLOSED)


def openclosed(lower, upper):
    """
    Create a left-open interval with given bounds.

    :param lower: value of the lower bound.
    :param upper: value of the upper bound.
    :return: an interval.
    """
    return Interval.from_atomic(Bound.OPEN, lower, upper, Bound.CLOSED)


def closedopen(lower, upper):
    """
    Create a right-open interval with given bounds.

    :param lower: value of the lower bound.
    :param upper: value of the upper bound.
    :return: an interval.
    """
    return Interval.from_atomic(Bound.CLOSED, lower, upper, Bound.OPEN)


def singleton(value):
    """
    Create a singleton interval.

    :param value: value of the lower and upper bounds.
    :return: an interval.
    """
    return Interval.from_atomic(Bound.CLOSED, value, value, Bound.CLOSED)


def empty():
    """
    Create an empty interval.

    :return: an interval.
    """
    return Interval.from_atomic(Bound.OPEN, inf, -inf, Bound.OPEN)


class Interval:
    """
    This class represents an interval.

    An interval is an (automatically simplified) union of atomic intervals.
    It can be created with Interval.from_atomic(), by passing intervals to __init__, or by using
    one of the helpers provided in this module (open, closed, openclosed, etc.)
    """

    __slots__ = ('_intervals',)

    def __init__(self, *intervals):
        """
        Create a disjunction of zero, one or more intervals.

        :param intervals: zero, one or more intervals.
        """
        self._intervals = list()

        for interval in intervals:
            if isinstance(interval, Interval):
                if not interval.empty:
                    self._intervals.extend(interval._intervals)
            else:
                raise TypeError('Parameters must be Interval instances')

        if len(self._intervals) == 0:
            # So we have at least one (empty) interval
            self._intervals.append(Atomic(Bound.OPEN, inf, -inf, Bound.OPEN))
        else:
            # Sort intervals by lower bound, closed first.
            self._intervals.sort(key=lambda i: (i.lower, i.left is Bound.OPEN))

            i = 0
            # Try to merge consecutive intervals
            while i < len(self._intervals) - 1:
                current = self._intervals[i]
                successor = self._intervals[i + 1]

                if mergeable(current, successor):
                    if current.lower == successor.lower:
                        lower = current.lower
                        left = current.left if current.left == Bound.CLOSED else successor.left
                    else:
                        lower = min(current.lower, successor.lower)
                        left = current.left if lower == current.lower else successor.left

                    if current.upper == successor.upper:
                        upper = current.upper
                        right = current.right if current.right == Bound.CLOSED else successor.right
                    else:
                        upper = max(current.upper, successor.upper)
                        right = current.right if upper == current.upper else successor.right

                    union = Atomic(left, lower, upper, right)
                    self._intervals.pop(i)  # pop current
                    self._intervals.pop(i)  # pop successor
                    self._intervals.insert(i, union)
                else:
                    i = i + 1

    @property
    def left(self):
        """
        Lowest left boundary is either CLOSED or OPEN.
        """
        return self._intervals[0].left

    @property
    def lower(self):
        """
        Lowest lower bound value.
        """
        return self._intervals[0].lower

    @property
    def upper(self):
        """
        Highest upper bound value.
        """
        return self._intervals[-1].upper

    @property
    def right(self):
        """
        Highest right boundary is either CLOSED or OPEN.
        """
        return self._intervals[-1].right

    @property
    def empty(self):
        """
        True if interval is empty, False otherwise.
        """
        return (
            self.lower > self.upper or
            (self.lower == self.upper and (self.left == Bound.OPEN or self.right == Bound.OPEN))
        )

    @property
    def atomic(self):
        """
        True if this interval is atomic, False otherwise.
        An interval is atomic if it is composed of a single (possibly empty) atomic interval.
        """
        return len(self._intervals) == 1

    @staticmethod
    def from_atomic(left, lower, upper, right):
        """
        Create an Interval instance containing a single atomic interval.

        :param left: either CLOSED or OPEN.
        :param lower: value of the lower bound.
        :param upper: value of the upper bound.
        :param right: either CLOSED or OPEN.
        """
        instance = Interval()
        left = left if lower not in [inf, -inf] else Bound.OPEN
        right = right if upper not in [inf, -inf] else Bound.OPEN

        instance._intervals = [Atomic(left, lower, upper, right)]
        if instance.empty:
            return Interval()

        return instance

    @property
    def enclosure(self):
        """
        Return the smallest interval composed of a single atomic interval that encloses
        the current interval.

        :return: an Interval instance.
        """
        return Interval.from_atomic(self.left, self.lower, self.upper, self.right)

    def replace(self, left=None, lower=None, upper=None, right=None, *, ignore_inf=True):
        """
        Create a new interval based on the current one and the provided values.

        If current interval is not atomic, it is extended or restricted such that
        its enclosure satisfies the new bounds. In other words, its new enclosure
        will be equal to self.enclosure.replace(left, lower, upper, right).

        Callable can be passed instead of values. In that case, it is called with the current
        corresponding value except if ignore_inf if set (default) and the corresponding
        bound is an infinity.

        :param left: (a function of) left boundary.
        :param lower: (a function of) value of the lower bound.
        :param upper: (a function of) value of the upper bound.
        :param right: (a function of) right boundary.
        :param ignore_inf: ignore infinities if functions are provided (default is True).
        :return: an Interval instance
        """
        enclosure = self.enclosure

        if callable(left):
            left = left(enclosure.left)
        else:
            left = enclosure.left if left is None else left

        if callable(lower):
            if ignore_inf and enclosure.lower in [-inf, inf]:
                lower = enclosure.lower
            else:
                lower = lower(enclosure.lower)
        else:
            lower = enclosure.lower if lower is None else lower

        if callable(upper):
            if ignore_inf and enclosure.upper in [-inf, inf]:
                upper = enclosure.upper
            else:
                upper = upper(enclosure.upper)
        else:
            upper = enclosure.upper if upper is None else upper

        if callable(right):
            right = right(enclosure.right)
        else:
            right = enclosure.right if right is None else right

        if self.atomic:
            return Interval.from_atomic(left, lower, upper, right)

        n_interval = self & Interval.from_atomic(left, lower, upper, right)

        if n_interval.atomic:
            return n_interval.replace(left, lower, upper, right)
        else:
            lowest = n_interval[0].replace(left=left, lower=lower)
            highest = n_interval[-1].replace(upper=upper, right=right)
            return Interval(lowest, *n_interval[1:-1], highest)

    def apply(self, func):
        """
        Apply a function on each of the underlying atomic intervals and return their union
        as a new interval instance

        Given function is expected to return an interval (possibly empty or not atomic) or
        a 4-uple (left, lower, upper, right) whose values correspond to the parameters of
        Interval.from_atomic(left, lower, upper, right).

        This method is merely a shortcut for Interval(*list(map(func, self))).

        :param func: function to apply on each underlying atomic interval.
        :return: an Interval instance.
        """
        intervals = []

        for i in self:
            value = func(i)

            if isinstance(value, Interval):
                intervals.append(value)
            elif isinstance(value, tuple):
                intervals.append(Interval.from_atomic(*value))
            else:
                raise TypeError('Unsupported return type {} for {}'.format(type(value), value))

        return Interval(*intervals)

    def adjacent(self, other):
        """
        Test if two intervals are adjacent.

        Two intervals are adjacent if they do not overlap and their union form a
        single atomic interval.

        While this definition corresponds to the usual notion of adjacency for atomic
        intervals, it has stronger requirements for non-atomic ones since it requires
        all underlying atomic intervals to be adjacent (i.e. that one
        interval fills the gaps between the atomic intervals of the other one).

        :param other: an interval.
        :return: True if intervals are adjacent, False otherwise.
        """
        return (self & other).empty and (self | other).atomic

    def overlaps(self, other):
        """
        Test if two intervals overlap (i.e. if their intersection is non-empty).

        :param other: an interval.
        :return: True if intervals overlap, False otherwise.
        """
        if isinstance(other, Interval):
            i_iter = iter(self)
            o_iter = iter(other)
            i_current = next(i_iter)
            o_current = next(o_iter)

            while i_current is not None and o_current is not None:
                if i_current < o_current:
                    i_current = next(i_iter, None)
                elif o_current < i_current:
                    o_current = next(o_iter, None)
                else:
                    return True
            return False
        else:
            raise TypeError('Unsupported type {} for {}'.format(type(other), other))

    def intersection(self, other):
        """
        Return the intersection of two intervals.

        :param other: an interval.
        :return: the intersection of the intervals.
        """
        return self & other

    def union(self, other):
        """
        Return the union of two intervals.

        :param other: an interval.
        :return: the union of the intervals.
        """
        return self | other

    def contains(self, item):
        """
        Test if given item is contained in this interval.
        This method accepts intervals and arbitrary comparable values.

        :param item: an interval or any arbitrary comparable value.
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

        :param other: an interval.
        :return: the difference of the intervals.
        """
        return self - other

    def __len__(self):
        return len(self._intervals)

    def __iter__(self):
        return iter([Interval.from_atomic(*i) for i in self._intervals])

    def __getitem__(self, item):
        if isinstance(item, slice):
            return [Interval.from_atomic(*i) for i in self._intervals[item]]
        else:
            return Interval.from_atomic(*self._intervals[item])

    def __and__(self, other):
        if not isinstance(other, Interval):
            return NotImplemented

        if self.atomic and other.atomic:
            if self.lower == other.lower:
                lower = self.lower
                left = self.left if self.left == Bound.OPEN else other.left
            else:
                lower = max(self.lower, other.lower)
                left = self.left if lower == self.lower else other.left

            if self.upper == other.upper:
                upper = self.upper
                right = self.right if self.right == Bound.OPEN else other.right
            else:
                upper = min(self.upper, other.upper)
                right = self.right if upper == self.upper else other.right

            return Interval.from_atomic(left, lower, upper, right)
        else:
            intersections = []

            i_iter = iter(self)
            o_iter = iter(other)
            i_current = next(i_iter)
            o_current = next(o_iter)

            while i_current is not None and o_current is not None:
                if i_current < o_current:
                    i_current = next(i_iter, None)
                elif o_current < i_current:
                    o_current = next(o_iter, None)
                else:
                    # i_current and o_current have an overlap
                    intersections.append(i_current & o_current)

                    if i_current <= o_current:
                        # o_current can still intersect next i
                        i_current = next(i_iter, None)
                    elif o_current <= i_current:
                        # i_current can still intersect next o
                        o_current = next(o_iter, None)
                    else:
                        assert False

            return Interval(*intersections)

    def __or__(self, other):
        if isinstance(other, Interval):
            return Interval(self, other)
        else:
            return NotImplemented

    def __contains__(self, item):
        if isinstance(item, Interval):
            if item.empty:
                return True
            elif self.atomic:
                left = item.lower > self.lower or (
                    item.lower == self.lower and
                    (item.left == self.left or self.left == Bound.CLOSED)
                )
                right = item.upper < self.upper or (
                    item.upper == self.upper and
                    (item.right == self.right or self.right == Bound.CLOSED)
                )
                return left and right
            else:
                selfiter = iter(self)
                current = next(selfiter)

                for other in item:
                    while current < other:
                        try:
                            current = next(selfiter)
                        except StopIteration:
                            return False

                    # here current and other could have an overlap
                    if other not in current:
                        return False
                return True
        else:
            # Item is a value
            for i in self._intervals:
                left = (item >= i.lower) if i.left == Bound.CLOSED else (item > i.lower)
                right = (item <= i.upper) if i.right == Bound.CLOSED else (item < i.upper)
                if left and right:
                    return True
            return False

    def __invert__(self):
        complements = [
            Interval.from_atomic(Bound.OPEN, -inf, self.lower, ~self.left),
            Interval.from_atomic(~self.right, self.upper, inf, Bound.OPEN)
        ]

        for i, j in zip(self._intervals[:-1], self._intervals[1:]):
            complements.append(
                Interval.from_atomic(~i.right, i.upper, j.lower, ~j.left)
            )

        return Interval(*complements)

    def __sub__(self, other):
        if isinstance(other, Interval):
            return self & ~other
        else:
            return NotImplemented

    def __eq__(self, other):
        if isinstance(other, Interval):
            if len(other._intervals) != len(self._intervals):
                return False

            for a, b in zip(self._intervals, other._intervals):
                eq = (
                    a.left == b.left and
                    a.lower == b.lower and
                    a.upper == b.upper and
                    a.right == b.right
                )
                if not eq:
                    return False
            return True
        else:
            return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Interval):
            if self.right == Bound.OPEN:
                return self.upper <= other.lower
            else:
                return self.upper < other.lower or \
                    (self.upper == other.lower and other.left == Bound.OPEN)
        else:
            return self.upper < other or (self.right == Bound.OPEN and self.upper == other)

    def __gt__(self, other):
        if isinstance(other, Interval):
            if self.left == Bound.OPEN:
                return self.lower >= other.upper
            else:
                return self.lower > other.upper or \
                    (self.lower == other.upper and other.right == Bound.OPEN)
        else:
            return self.lower > other or (self.left == Bound.OPEN and self.lower == other)

    def __le__(self, other):
        if isinstance(other, Interval):
            if self.right == Bound.OPEN:
                return self.upper <= other.upper
            else:
                return self.upper < other.upper or \
                    (self.upper == other.upper and other.right == Bound.CLOSED)
        else:
            return self.lower < other or (self.left == Bound.CLOSED and self.lower == other)

    def __ge__(self, other):
        if isinstance(other, Interval):
            if self.left == Bound.OPEN:
                return self.lower >= other.lower
            else:
                return self.lower > other.lower or \
                    (self.lower == other.lower and other.left == Bound.CLOSED)
        else:
            return self.upper > other or (self.right == Bound.CLOSED and self.upper == other)

    def __hash__(self):
        return hash(tuple([self.lower, self.upper]))

    def __repr__(self):
        intervals = []

        for interval in self:
            if interval.empty:
                intervals.append('()')
            elif interval.lower == interval.upper:
                intervals.append('[{}]'.format(repr(interval.lower)))
            else:
                intervals.append(
                    '{}{},{}{}'.format(
                        '[' if interval.left == Bound.CLOSED else '(',
                        repr(interval.lower),
                        repr(interval.upper),
                        ']' if interval.right == Bound.CLOSED else ')',
                    )
                )
        return ' | '.join(intervals)