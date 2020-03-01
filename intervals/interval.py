from .const import Bound, inf


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
    if not hasattr(empty, '_instance'):
        empty._instance = Interval.from_atomic(Bound.OPEN, inf, -inf, Bound.OPEN)
    return empty._instance


class AtomicInterval:
    """
    This class represents an atomic interval.

    An atomic interval is a single interval, with a lower and an upper bound,
    and two (closed or open) boundaries.

    This class is NOT part of the public API.
    """

    __slots__ = ('_left', '_lower', '_upper', '_right')

    def __init__(self, left, lower, upper, right):
        """
        Create an atomic interval.

        If a bound is set to infinity (regardless of its sign), the corresponding boundary will
        be exclusive.

        :param left: either CLOSED or OPEN.
        :param lower: value of the lower bound.
        :param upper: value of the upper bound.
        :param right: either CLOSED or OPEN.
        """
        self._left = left if lower not in [inf, -inf] else Bound.OPEN
        self._lower = lower
        self._upper = upper
        self._right = right if upper not in [inf, -inf] else Bound.OPEN

    @property
    def left(self):
        """
        Left boundary is either CLOSED or OPEN.
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
        Right boundary is either CLOSED or OPEN.
        """
        return self._right

    def mergeable(self, other):
        """
        Test if given atomic interval can be merged with current one.
        Two intervals are mergeable if their union is an atomic interval
        (i.e. they overlap or are adjacent).

        :param other: an atomic interval.
        :return: True if mergeable, False otherwise.
        """
        if not isinstance(other, AtomicInterval):
            raise TypeError('Only AtomicInterval instances are supported.')

        if self._lower < other.lower or (self._lower == other.lower and self._left == Bound.CLOSED):
            first, second = self, other
        else:
            first, second = other, self

        if first._upper == second._lower:
            return first._right == Bound.CLOSED or second._left == Bound.CLOSED

        return first._upper > second._lower

    def __and__(self, other):
        if isinstance(other, AtomicInterval):
            if self._lower == other._lower:
                lower = self._lower
                left = self._left if self._left == Bound.OPEN else other._left
            else:
                lower = max(self._lower, other._lower)
                left = self._left if lower == self._lower else other._left

            if self._upper == other._upper:
                upper = self._upper
                right = self._right if self._right == Bound.OPEN else other._right
            else:
                upper = min(self._upper, other._upper)
                right = self._right if upper == self._upper else other._right

            if lower <= upper:
                return AtomicInterval(left, lower, upper, right)
            else:
                return AtomicInterval(Bound.OPEN, lower, lower, Bound.OPEN)
        else:
            return NotImplemented

    def __or__(self, other):
        if isinstance(other, AtomicInterval):
            if self.mergeable(other):
                if self._lower == other._lower:
                    lower = self._lower
                    left = self._left if self._left == Bound.CLOSED else other._left
                else:
                    lower = min(self._lower, other._lower)
                    left = self._left if lower == self._lower else other._left

                if self._upper == other._upper:
                    upper = self._upper
                    right = self._right if self._right == Bound.CLOSED else other._right
                else:
                    upper = max(self._upper, other._upper)
                    right = self._right if upper == self._upper else other._right

                return [AtomicInterval(left, lower, upper, right)]
            else:
                return [self, other]
        else:
            return NotImplemented


class Interval:
    """
    This class represents an interval.

    An interval is an (automatically simplified) union of atomic intervals.
    It can be created with Interval.from_atomic(), or by passing intervals to __init__, or by using
    one of the helpers provided in this module (open, closed, openclosed, etc.)
    """

    __slots__ = ('_intervals',)

    def __init__(self, *intervals):
        """
        Create an interval from a list of intervals.

        :param intervals: a list of intervals.
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
            self._intervals.append(AtomicInterval(Bound.OPEN, inf, -inf, Bound.OPEN))
        else:
            # Sort intervals by lower bound
            self._intervals.sort(key=lambda i: i.lower)

            i = 0
            # Attempt to merge consecutive intervals
            while i < len(self._intervals) - 1:
                current = self._intervals[i]
                successor = self._intervals[i + 1]

                union = (current | successor)
                if len(union) == 1:
                    self._intervals.pop(i)  # pop current
                    self._intervals.pop(i)  # pop successor
                    self._intervals.insert(i, union[0])
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

        instance._intervals = [AtomicInterval(left, lower, upper, right)]
        if instance.empty:
            instance._intervals = [AtomicInterval(Bound.OPEN, inf, -inf, Bound.OPEN)]

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
            return Interval(*[lowest] + n_interval[1:-1] + [highest])

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
        Test if given interval is adjacent.

        An interval is adjacent if there is no intersection, and their union is an atomic interval.

        :param other: an interval.
        :return: True if intervals are adjacent, False otherwise.
        """
        return (self & other).empty and (self | other).atomic

    def overlaps(self, other):
        """
        Test if intervals have any overlapping value.

        :param other: an interval.
        :return: True if intervals overlap, False otherwise.
        """
        if isinstance(other, Interval):
            return not (self & other).empty
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
        return iter([Interval.from_atomic(i.left, i.lower, i.upper, i.right) for i in self._intervals])

    def __getitem__(self, item):
        if isinstance(item, slice):
            return [Interval.from_atomic(i.left, i.lower, i.upper, i.right) for i in self._intervals[item]]
        else:
            i = self._intervals[item]
            return Interval.from_atomic(i.left, i.lower, i.upper, i.right)

    def __and__(self, other):
        if isinstance(other, Interval):
            new_intervals = []
            for interval in self._intervals:
                for o_interval in other._intervals:
                    if interval.lower == o_interval.lower:
                        lower = interval.lower
                        left = interval.left if interval.left == Bound.OPEN else o_interval.left
                    else:
                        lower = max(interval.lower, o_interval.lower)
                        left = interval.left if lower == interval.lower else o_interval.left

                    if interval.upper == o_interval.upper:
                        upper = interval.upper
                        right = interval.right if interval.right == Bound.OPEN else o_interval.right
                    else:
                        upper = min(interval.upper, o_interval.upper)
                        right = interval.right if upper == interval.upper else o_interval.right

                    if lower <= upper:
                        new_intervals.append(Interval.from_atomic(left, lower, upper, right))
                    else:
                        new_intervals.append(Interval.from_atomic(Bound.OPEN, lower, lower, Bound.OPEN))
            return Interval(*new_intervals)
        else:
            return NotImplemented

    def __or__(self, other):
        if isinstance(other, Interval):
            return Interval(self, other)
        else:
            return NotImplemented

    def __contains__(self, item):
        if self.atomic:
            if isinstance(item, Interval):
                left = item.lower > self.lower or (
                    item.lower == self.lower and (item.left == self.left or self.left == Bound.CLOSED)
                )
                right = item.upper < self.upper or (
                    item.upper == self.upper and (item.right == self.right or self.right == Bound.CLOSED)
                )
                return left and right
            else:
                left = (item >= self.lower) if self.left == Bound.CLOSED else (item > self.lower)
                right = (item <= self.upper) if self.right == Bound.CLOSED else (item < self.upper)
                return left and right
        else:
            for interval in self:
                if item in interval:
                    return True
            return False

    def __invert__(self):
        complements = []
        for i in self._intervals:
            complements.append(Interval(
                Interval.from_atomic(Bound.OPEN, -inf, i.lower, ~i._left),
                Interval.from_atomic(~i._right, i._upper, inf, Bound.OPEN)
            ))

        intersection = complements[0]
        for i in complements[1:]:
            intersection = intersection & i

        return intersection

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
        if self.empty:
            return '()'
        elif self.lower == self.upper:
            return '[{}]'.format(repr(self.lower))
        else:
            return ' | '.join(
                '{}{},{}{}'.format(
                    '[' if i.left == Bound.CLOSED else '(',
                    repr(i.lower),
                    repr(i.upper),
                    ']' if i.right == Bound.CLOSED else ')',
                )
                for i in self._intervals
            )

