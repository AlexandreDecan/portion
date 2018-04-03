from functools import total_ordering
from itertools import combinations


@total_ordering
class PInf:
    """
    Use to represent positive infinity.
    """

    def __neg__(self):
        return NInf()

    def __lt__(self, o):
        return isinstance(o, PInf)

    def __eq__(self, o):
        return isinstance(o, PInf)

    def __repr__(self):
        return '+inf'


@total_ordering
class NInf:
    """
    Use to represent negative infinity.
    """

    def __neg__(self):
        return PInf()

    def __gt__(self, o):
        return isinstance(o, NInf)

    def __eq__(self, o):
        return isinstance(o, NInf)

    def __repr__(self):
        return '-inf'


INF = PInf()
OPEN = 0
CLOSED = 1


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
    Support equality (=), intersection (&), union (|) and containment (in).
    """

    def __init__(self, left, lower, upper, right):
        if lower > upper:
            raise ValueError('Bounds are not ordered correctly: lower bound {} must be smaller than upper bound {}'.format(lower, upper))
        self.left = left
        self.lower = lower
        self.upper = upper
        self.right = right

    def is_empty(self):
        return self.lower == self.upper and (self.left == OPEN or self.right == OPEN)

    def overlaps(self, other, permissive=False):
        """
        Return True if sets have any overlapping value.
        If 'permissive' is set to True, it considers [1, 2) and [2, 3] as an
        overlap on value 2, not [1, 2) and (2, 3].
        """
        if self.lower > other.lower:
            first, second = other, self
        else:
            first, second = self, other
         
        if first.upper == second.lower:
            if permissive:
                return first.right == CLOSED or second.right == CLOSED
            else:
                return first.right == CLOSED and second.right == CLOSED
         
        return first.upper > second.lower

    def intersection(self, other):
        if isinstance(other, AtomicInterval):
            if self.lower == other.lower:
                lower = self.lower
                left = self.left if self.left == OPEN else other.left
            else:
                lower = max(self.lower, other.lower)
                left = self.left if lower == self.lower else other.left
                
            if self.upper == other.upper:
                upper = self.upper
                right = self.right if self.right == OPEN else other.right
            else:
                upper = min(self.upper, other.upper)
                right = self.right if upper == self.upper else other.right
            
            if lower <= upper:
                return AtomicInterval(left, lower, upper, right)
            else:
                return AtomicInterval(OPEN, lower, lower, OPEN)
        else:
            return NotImplemented

    def union(self, other):
        if isinstance(other, AtomicInterval):
            if self.overlaps(other, permissive=True):
                if self.lower == other.lower:
                    lower = self.lower
                    left = self.left if self.left == OPEN else other.left
                else:
                    lower = min(self.lower, other.lower)
                    left = self.left if lower == self.lower else other.left
                    
                if self.upper == other.upper:
                    upper = self.upper
                    right = self.right if self.right == OPEN else other.right
                else:
                    upper = max(self.upper, other.upper)
                    right = self.right if upper == self.upper else other.right
                
                return AtomicInterval(left, lower, upper, right)
            else:
                return Interval(self, other)
        else:
            return NotImplemented

    def contains(self, item):
        """
        Return True if given item is contained in this atomic interval.
        Item must be either a value, an AtomicInterval or an Interval.
        :param item: a value, an AtomicInterval or an Interval
        :return: True if given item is contained in this atomic interval.
        """
        if isinstance(item, AtomicInterval):
            left = item.lower > self.lower or (item.lower == self.lower and (item.left == self.left or self.left == CLOSED))
            right = item.upper < self.upper or (item.upper == self.upper and (item.right == self.right or self.right == CLOSED))
            return left and right
        elif isinstance(item, Interval):
            return item.to_atomic() in self
        else:
            left = (item >= self.lower) if self.left == CLOSED else (item > self.lower)
            right = (item <= self.upper) if self.right == CLOSED else (item < self.upper)
            return left and right

    def __and__(self, other):
        return self.intersection(other)

    def __or__(self, other):
        return self.union(other)

    def __contains__(self, item):
        return self.contains(item)

    def __eq__(self, other):
        if isinstance(other, AtomicInterval):
            return (
                self.left == other.left and
                self.lower == other.lower and
                self.upper == other.upper and
                self.right == other.right
            )
        elif isinstance(other, Interval):
            return other.is_atomic() and self == other.to_atomic()
        else:
            return NotImplemented

    def __hash__(self):
        try:
            return hash(self.lower)
        except TypeError:
            return 0

    def __repr__(self):
        if self.is_empty():
            return '()'

        return '{}{},{}{}'.format(
            '[' if self.left == CLOSED else ']',
            repr(self.lower),
            repr(self.upper),
            ']' if self.right == CLOSED else '[',
        )


class Interval:
    """
    Represent an interval (union of atomic intervals).
    Consider using open, closed, openclosed or closedopen to create an Interval.

    Support equality (=), intersection (&), union (|), containment (in) and iteration (on AtomicInterval).
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
            self._intervals.add(AtomicInterval(OPEN, INF, INF, OPEN))

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
            raise ValueError('Parameter must be an Interval or an AtomicInterval')

    def intersection(self, other):
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

    def union(self, other):
        if isinstance(other, AtomicInterval):
            return self | Interval(other)
        elif isinstance(other, Interval):
            return Interval(*(list(self._intervals) + list(other._intervals)))
        else:
            return NotImplemented

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

    def __len__(self):
        return len([i for i in self._intervals if not i.is_empty()])
    
    def __iter__(self):
        return [i for i in self._intervals if not i.is_empty()]

    def __and__(self, other):
        return self.intersection(other)

    def __or__(self, other):
        return self.union(other)

    def __contains__(self, item):
        return self.contains(item)

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
