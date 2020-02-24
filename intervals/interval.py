from .const import Bound, inf


def open(lower, upper):
    """
    Create an open interval with given bounds.
    """
    return Interval(AtomicInterval(Bound.OPEN, lower, upper, Bound.OPEN))


def closed(lower, upper):
    """
    Create a closed interval with given bounds.
    """
    return Interval(AtomicInterval(Bound.CLOSED, lower, upper, Bound.CLOSED))


def openclosed(lower, upper):
    """
    Create an left-open interval with given bounds.
    """
    return Interval(AtomicInterval(Bound.OPEN, lower, upper, Bound.CLOSED))


def closedopen(lower, upper):
    """
    Create an right-open interval with given bounds.
    """
    return Interval(AtomicInterval(Bound.CLOSED, lower, upper, Bound.OPEN))


def singleton(value):
    """
    Create a singleton.
    """
    return Interval(AtomicInterval(Bound.CLOSED, value, value, Bound.CLOSED))


def empty():
    """
    Create an empty set.
    """
    if not hasattr(empty, '_instance'):
        empty._instance = Interval(AtomicInterval(Bound.OPEN, inf, -inf, Bound.OPEN))
    return empty._instance


class AtomicInterval:
    """
    This class represents an atomic interval.

    An atomic interval is a single interval, with a lower and upper bounds,
    and two (closed or open) boundaries.
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

        if self.empty:
            self._left = Bound.OPEN
            self._lower = inf
            self._upper = -inf
            self._right = Bound.OPEN

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

    @property
    def empty(self):
        """
        True if interval is empty, False otherwise.
        """
        return (
            self._lower > self._upper or
            (self._lower == self._upper and (self._left == Bound.OPEN or self._right == Bound.OPEN))
        )

    def replace(self, left=None, lower=None, upper=None, right=None, *, ignore_inf=True):
        """
        Create a new interval based on the current one and the provided values.

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
        if callable(left):
            left = left(self._left)
        else:
            left = self._left if left is None else left

        if callable(lower):
            lower = self._lower if ignore_inf and self._lower in [-inf, inf] else lower(self._lower)
        else:
            lower = self._lower if lower is None else lower

        if callable(upper):
            upper = self._upper if ignore_inf and self._upper in [-inf, inf] else upper(self._upper)
        else:
            upper = self._upper if upper is None else upper

        if callable(right):
            right = right(self._right)
        else:
            right = self._right if right is None else right

        return AtomicInterval(left, lower, upper, right)

    def overlaps(self, other, *, adjacent=False):
        """
        Test if intervals have any overlapping value.

        If 'adjacent' is set to True (default is False), then it returns True for adjacent
        intervals as well (e.g., [1, 2) and [2, 3], but not [1, 2) and (2, 3]).
        This is useful to see whether two intervals can be merged or not.

        :param other: an atomic interval.
        :param adjacent: set to True to accept adjacent intervals as well.
        :return: True if intervals overlap, False otherwise.
        """
        if not isinstance(other, AtomicInterval):
            raise TypeError('Only AtomicInterval instances are supported.')

        if self._lower < other.lower or (self._lower == other.lower and self._left == Bound.CLOSED):
            first, second = self, other
        else:
            first, second = other, self

        if first._upper == second._lower:
            if adjacent:
                return first._right == Bound.CLOSED or second._left == Bound.CLOSED
            else:
                return first._right == Bound.CLOSED and second._left == Bound.CLOSED

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
        Return the union of two intervals. If the union cannot be represented using a single
        atomic interval, return an Interval instance (which corresponds to an union of atomic
        intervals).

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
            if self.overlaps(other, adjacent=True):
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

                return AtomicInterval(left, lower, upper, right)
            else:
                return Interval(self, other)
        else:
            return NotImplemented

    def __contains__(self, item):
        if isinstance(item, AtomicInterval):
            left = item._lower > self._lower or (
                item._lower == self._lower and (item._left == self._left or self._left == Bound.CLOSED)
            )
            right = item._upper < self._upper or (
                item._upper == self._upper and (item._right == self._right or self._right == Bound.CLOSED)
            )
            return left and right
        elif isinstance(item, Interval):
            for interval in item:
                if interval not in self:
                    return False
            return True
        else:
            left = (item >= self._lower) if self._left == Bound.CLOSED else (item > self._lower)
            right = (item <= self._upper) if self._right == Bound.CLOSED else (item < self._upper)
            return left and right

    def __invert__(self):
        return Interval(
            AtomicInterval(Bound.OPEN, -inf, self._lower, ~self._left),
            AtomicInterval(~self._right, self._upper, inf, Bound.OPEN)
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
            if self._right == Bound.OPEN:
                return self._upper <= other._lower
            else:
                return self._upper < other._lower or \
                    (self._upper == other._lower and other._left == Bound.OPEN)
        elif isinstance(other, Interval):
            return self < other.to_atomic()
        else:
            return self._upper < other or (self._right == Bound.OPEN and self._upper == other)

    def __gt__(self, other):
        if isinstance(other, AtomicInterval):
            if self._left == Bound.OPEN:
                return self._lower >= other._upper
            else:
                return self._lower > other._upper or \
                    (self._lower == other._upper and other._right == Bound.OPEN)
        elif isinstance(other, Interval):
            return self > other.to_atomic()
        else:
            return self._lower > other or (self._left == Bound.OPEN and self._lower == other)

    def __le__(self, other):
        if isinstance(other, AtomicInterval):
            if self._right == Bound.OPEN:
                return self._upper <= other._upper
            else:
                return self._upper < other._upper or \
                    (self._upper == other._upper and other._right == Bound.CLOSED)
        elif isinstance(other, Interval):
            return self <= other.to_atomic()
        else:
            return self._lower < other or (self._left == Bound.CLOSED and self._lower == other)

    def __ge__(self, other):
        if isinstance(other, AtomicInterval):
            if self._left == Bound.OPEN:
                return self._lower >= other._lower
            else:
                return self._lower > other._lower or \
                    (self._lower == other._lower and other._left == Bound.CLOSED)
        elif isinstance(other, Interval):
            return self >= other.to_atomic()
        else:
            return self._upper > other or (self._right == Bound.CLOSED and self._upper == other)

    def __hash__(self):
        return hash((self._lower, self._upper))

    def __repr__(self):
        if self.empty:
            return '()'
        elif self._lower == self._upper:
            return '[{}]'.format(repr(self._lower))
        else:
            return '{}{},{}{}'.format(
                '[' if self._left == Bound.CLOSED else '(',
                repr(self._lower),
                repr(self._upper),
                ']' if self._right == Bound.CLOSED else ')',
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
                if not interval.empty:
                    self._intervals.extend(interval)
            elif isinstance(interval, AtomicInterval):
                if not interval.empty:
                    self._intervals.append(interval)
            else:
                raise TypeError('Parameters must be Interval or AtomicInterval instances')

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

                if current.overlaps(successor, adjacent=True):
                    interval = current | successor
                    self._intervals.pop(i)  # pop current
                    self._intervals.pop(i)  # pop successor
                    self._intervals.insert(i, interval)
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
        return self.atomic and self._intervals[0].empty

    @property
    def atomic(self):
        """
        True if this interval is atomic, False otherwise.
        An interval is atomic if it is composed of a single atomic interval.
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
        Return the smallest interval composed of a single atomic interval that encloses
        the current interval. This method is equivalent to Interval(self.to_atomic())

        :return: an Interval instance.
        """
        return Interval(self.to_atomic())

    def replace(self, left=None, lower=None, upper=None, right=None, *, ignore_inf=True):
        """
        Create a new interval based on the current one and the provided values.

        If current interval is not atomic, it is extended or restricted such that
        its enclosure satisfies the new bounds. In other words, its new enclosure
        will be equal to self.to_atomic().replace(left, lower, upper, right).

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
        enclosure = self.to_atomic()

        if callable(left):
            left = left(enclosure._left)
        else:
            left = enclosure._left if left is None else left

        if callable(lower):
            if ignore_inf and enclosure._lower in [-inf, inf]:
                lower = enclosure._lower
            else:
                lower = lower(enclosure._lower)
        else:
            lower = enclosure._lower if lower is None else lower

        if callable(upper):
            if ignore_inf and enclosure._upper in [-inf, inf]:
                upper = enclosure._upper
            else:
                upper = upper(enclosure._upper)
        else:
            upper = enclosure._upper if upper is None else upper

        if callable(right):
            right = right(enclosure._right)
        else:
            right = enclosure._right if right is None else right

        n_interval = self & AtomicInterval(left, lower, upper, right)

        if len(n_interval) > 1:
            lowest = n_interval[0].replace(left=left, lower=lower)
            highest = n_interval[-1].replace(upper=upper, right=right)
            return Interval(*[lowest] + n_interval[1:-1] + [highest])
        else:
            return Interval(n_interval[0].replace(left, lower, upper, right))

    def apply(self, func):
        """
        Apply given function on each of the underlying AtomicInterval instances and return a new
        Interval instance. The function is expected to return an AtomicInterval, an Interval
        or a 4-uple (left, lower, upper, right).

        :param func: function to apply on each of the underlying AtomicInterval instances.
        :return: an Interval instance.
        """
        intervals = []

        for interval in self:
            value = func(interval)

            if isinstance(value, (Interval, AtomicInterval)):
                intervals.append(value)
            elif isinstance(value, tuple):
                intervals.append(AtomicInterval(*value))
            else:
                raise TypeError('Unsupported return type {} for {}'.format(type(value), value))

        return Interval(*intervals)

    def adjacent(self, other):
        """
        Test if given interval is adjacent.

        An interval is adjacent if there is no intersection, and their union is an atomic interval.

        :param other: an interval or atomic interval.
        :return: True if intervals are adjacent, False otherwise.
        """
        return (self & other).empty and (self | other).atomic

    def overlaps(self, other, *, adjacent=False):
        """
        Test if intervals have any overlapping value.

        If 'adjacent' is set to True (default is False), then it returns True for adjacent
        intervals as well (e.g., [1, 2) and [2, 3], but not [1, 2) and (2, 3]).
        This is useful to see whether two intervals can be merged or not.

        :param other: an interval or atomic interval.
        :param adjacent: set to True to accept adjacent intervals as well.
        :return: True if intervals overlap, False otherwise.
        """
        if isinstance(other, AtomicInterval):
            for interval in self._intervals:
                if interval.overlaps(other, adjacent=adjacent):
                    return True
            return False
        elif isinstance(other, Interval):
            for o_interval in other._intervals:
                if self.overlaps(o_interval, adjacent=adjacent):
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
        return len(self._intervals)

    def __iter__(self):
        return iter(self._intervals)

    def __getitem__(self, item):
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

    def __lt__(self, other):
        return self.to_atomic() < other

    def __gt__(self, other):
        return self.to_atomic() > other

    def __le__(self, other):
        return self.to_atomic() <= other

    def __ge__(self, other):
        return self.to_atomic() >= other

    def __hash__(self):
        return hash(tuple(self._intervals))
        return hash(self._intervals[0])

    def __repr__(self):
        return ' | '.join(repr(i) for i in self._intervals)
