import pytest

import intervals as I
from intervals.interval import Interval


class TestHelpers:
    def test_bounds(self):
        assert I.closed(0, 1) == Interval.from_atomic(I.CLOSED, 0, 1, I.CLOSED)
        assert I.open(0, 1) == Interval.from_atomic(I.OPEN, 0, 1, I.OPEN)
        assert I.openclosed(0, 1) == Interval.from_atomic(I.OPEN, 0, 1, I.CLOSED)
        assert I.closedopen(0, 1) == Interval.from_atomic(I.CLOSED, 0, 1, I.OPEN)
        assert I.singleton(2) == I.closed(2, 2)

    def test_with_infinities(self):
        assert I.closed(-I.inf, I.inf) == I.open(-I.inf, I.inf)
        assert I.closed(-I.inf, 0) == I.openclosed(-I.inf, 0)
        assert I.closed(0, I.inf) == I.closedopen(0, I.inf)

    def test_empty(self):
        assert I.empty() == Interval.from_atomic(I.OPEN, I.inf, -I.inf, I.open)
        assert I.closed(3, -3) == I.empty()

        assert I.openclosed(0, 0) == I.empty()
        assert I.closedopen(0, 0) == I.empty()
        assert I.open(0, 0) == I.empty()
        assert I.closed(0, 0) != I.empty()

        assert I.singleton(I.inf) == I.empty()
        assert I.singleton(-I.inf) == I.empty()

    def test_empty_is_singleton(self):
        assert I.empty() is I.empty()


class TestInterval:
    def test_creation(self):
        assert I.Interval() == I.empty()
        assert I.Interval(I.closed(0, 1)) == I.closed(0, 1)
        assert I.Interval(I.closed(0, 1)) == I.closed(0, 1)
        assert I.Interval(I.closed(0, 1), I.closed(2, 3)) == I.closed(0, 1) | I.closed(2, 3)
        assert I.Interval(I.closed(0, 1) | I.closed(2, 3)) == I.closed(0, 1) | I.closed(2, 3)

        with pytest.raises(TypeError):
            I.Interval(1)

    def test_creation_issue_19(self):
        # https://github.com/AlexandreDecan/python-intervals/issues/19
        assert I.Interval(I.empty(), I.empty()) == I.empty()

    def test_bounds(self):
        i = I.openclosed(1, 2)
        assert i.left == I.OPEN
        assert i.right == I.CLOSED
        assert i.lower == 1
        assert i.upper == 2

    def test_bounds_on_empty(self):
        i = I.empty()
        assert i.left == I.OPEN
        assert i.right == I.OPEN
        assert i.lower == I.inf
        assert i.upper == -I.inf

        i = I.openclosed(10, -10)
        assert i.left == I.OPEN
        assert i.right == I.OPEN
        assert i.lower == I.inf
        assert i.upper == -I.inf

        i = I.open(0, 1) | I.closed(3, 4)
        assert i.left == I.OPEN
        assert i.right == I.CLOSED
        assert i.lower == 0
        assert i.upper == 4

    def test_bounds_on_union(self):
        i = I.closedopen(0, 1) | I.openclosed(3, 4)
        assert i.left == I.CLOSED
        assert i.right == I.CLOSED
        assert i.lower == 0
        assert i.upper == 4

    def test_is_empty(self):
        assert I.openclosed(1, 1).empty
        assert I.closedopen(1, 1).empty
        assert I.open(1, 1).empty
        assert not I.closed(1, 1).empty
        assert I.Interval().empty
        assert I.empty().empty

    def test_hash_with_hashable(self):
        assert hash(I.closed(0, 1)) is not None
        assert hash(I.closed(0, 1)) != hash(I.closed(1, 2))

        assert hash(I.openclosed(-I.inf, 0)) is not None
        assert hash(I.closedopen(0, I.inf)) is not None
        assert hash(I.empty()) is not None

        assert hash(I.closed(0, 1) | I.closed(3, 4)) is not None
        assert hash(I.closed(0, 1) | I.closed(3, 4)) != hash(I.closed(0, 1))
        assert hash(I.closed(0, 1) | I.closed(3, 4)) != hash(I.closed(3, 4))

    def test_hash_with_unhashable(self):
        # Let's create a comparable but no hashable object
        class T(int):
            def __hash__(self):
                raise TypeError()

        x = I.closed(T(1), T(2))
        with pytest.raises(TypeError):
            hash(x)

        y = x | I.closed(3, 4)
        with pytest.raises(TypeError):
            hash(y)

    def test_enclosure(self):
        assert I.closed(0, 1) == I.closed(0, 1).enclosure
        assert I.open(0, 1) == I.open(0, 1).enclosure
        assert I.closed(0, 4) == (I.closed(0, 1) | I.closed(3, 4)).enclosure
        assert I.openclosed(0, 4) == (I.open(0, 1) | I.closed(3, 4)).enclosure


class TestIntervalReplace:
    def test_replace_bounds(self):
        i = I.open(-I.inf, I.inf)
        assert i.replace(lower=lambda v: 1, upper=lambda v: 1) == I.open(-I.inf, I.inf)
        assert i.replace(lower=lambda v: 1, upper=lambda v: 2, ignore_inf=False) == I.open(1, 2)

    def test_replace_values(self):
        i = I.open(0, 1)
        assert i.replace(left=I.CLOSED, right=I.CLOSED) == I.closed(0, 1)
        assert i.replace(lower=1, upper=2) == I.open(1, 2)
        assert i.replace(lower=lambda v: 1, upper=lambda v: 2) == I.open(1, 2)

    def test_replace_values_on_infinities(self):
        i = I.open(-I.inf, I.inf)
        assert i.replace(lower=lambda v: 1, upper=lambda v: 2) == i
        assert i.replace(lower=lambda v: 1, upper=lambda v: 2, ignore_inf=False) == I.open(1, 2)

    def test_replace_with_union(self):
        i = I.closed(0, 1) | I.open(2, 3)
        assert i.replace() == i
        assert i.replace(I.OPEN, -1, 4, I.OPEN) == I.openclosed(-1, 1) | I.open(2, 4)
        assert i.replace(lower=2) == I.closedopen(2, 3)
        assert i.replace(upper=1) == I.closedopen(0, 1)
        assert i.replace(lower=5) == I.empty()
        assert i.replace(upper=-5) == I.empty()
        assert i.replace(left=lambda v: ~v, lower=lambda v: v - 1, upper=lambda v: v + 1, right=lambda v: ~v) == I.openclosed(-1, 1) | I.openclosed(2, 4)

    def test_replace_with_empty(self):
        assert I.empty().replace(left=I.CLOSED, right=I.CLOSED) == I.empty()
        assert I.empty().replace(lower=1, upper=2) == I.open(1, 2)
        assert I.empty().replace(lower=lambda v: 1, upper=lambda v: 2) == I.empty()
        assert I.empty().replace(lower=lambda v: 1, upper=lambda v: 2, ignore_inf=False) == I.open(1, 2)


class TestIntervalApply:
    def test_apply(self):
        i = I.closed(0, 1)
        assert i.apply(lambda s: s) == i
        assert i.apply(lambda s: (I.OPEN, -1, 2, I.OPEN)) == I.open(-1, 2)
        assert i.apply(lambda s: Interval.from_atomic(I.OPEN, -1, 2, I.OPEN)) == I.open(-1, 2)
        assert i.apply(lambda s: I.open(-1, 2)) == I.open(-1, 2)

    def test_apply_on_unions(self):
        i = I.closed(0, 1) | I.closed(2, 3)
        assert i.apply(lambda s: s) == i
        assert i.apply(lambda s: (I.OPEN, -1, 2, I.OPEN)) == I.open(-1, 2)
        assert i.apply(lambda s: (~s.left, s.lower - 1, s.upper - 1, ~s.right)) == I.open(-1, 0) | I.open(1, 2)
        assert i.apply(lambda s: Interval.from_atomic(I.OPEN, -1, 2, I.OPEN)) == I.open(-1, 2)
        assert i.apply(lambda s: I.open(-1, 2)) == I.open(-1, 2)

        assert i.apply(lambda s: (s.left, s.lower, s.upper * 2, s.right)) == I.closed(0, 6)

    def test_apply_on_empty(self):
        assert I.empty().apply(lambda s: (I.CLOSED, 1, 2, I.CLOSED)) == I.closed(1, 2)

    def test_apply_with_incorrect_types(self):
        i = I.closed(0, 1)
        with pytest.raises(TypeError):
            i.apply(lambda s: None)

        with pytest.raises(TypeError):
            i.apply(lambda s: 'unsupported')


class TestIntervalAdjacent():
    def test_adjacent(self):
        assert I.closedopen(0, 1).adjacent(I.closedopen(1, 2))
        assert I.closed(0, 1).adjacent(I.open(1, 2))
        assert not I.closed(0, 1).adjacent(I.closed(1, 2))
        assert not I.open(0, 1).adjacent(I.open(1, 2))

    def test_reversed_adjacent(self):
        assert I.closedopen(1, 2).adjacent(I.closedopen(0, 1))
        assert I.open(1, 2).adjacent(I.closed(0, 1))
        assert not I.closed(1, 2).adjacent(I.closed(0, 1))
        assert not I.open(1, 2).adjacent(I.open(0, 1))

    def test_non_adjacent(self):
        assert not I.closedopen(0, 1).adjacent(I.closedopen(3, 4))
        assert not I.closed(0, 1).adjacent(I.open(3, 4))
        assert not I.closed(0, 1).adjacent(I.closed(3, 4))
        assert not I.open(0, 1).adjacent(I.open(3, 4))

        assert not I.closedopen(3, 4).adjacent(I.closedopen(0, 1))
        assert not I.open(3, 4).adjacent(I.closed(0, 1))
        assert not I.closed(3, 4).adjacent(I.closed(0, 1))
        assert not I.open(3, 4).adjacent(I.open(0, 1))

    def test_overlapping(self):
        assert not I.openclosed(0, 2).adjacent(I.closedopen(2, 3))
        assert not I.closed(0, 2).adjacent(I.closedopen(2, 3))
        assert not I.closed(0, 2).adjacent(I.closed(2, 3))
        assert not I.open(0, 2).adjacent(I.open(2, 3))

        assert not I.closedopen(2, 3).adjacent(I.openclosed(0, 2))
        assert not I.closedopen(2, 3).adjacent(I.closed(0, 2))
        assert not I.closed(2, 3).adjacent(I.closed(0, 2))
        assert not I.open(2, 3).adjacent(I.open(0, 2))

    def test_contained(self):
        assert not I.closed(0, 4).adjacent(I.closed(0, 2))
        assert not I.closed(0, 4).adjacent(I.closed(2, 4))
        assert not I.closed(0, 4).adjacent(I.open(0, 2))
        assert not I.closed(0, 4).adjacent(I.open(2, 4))

        assert not I.closed(0, 2).adjacent(I.closed(0, 4))
        assert not I.closed(2, 4).adjacent(I.closed(0, 4))
        assert not I.closed(0, 2).adjacent(I.open(0, 4))
        assert not I.closed(2, 4).adjacent(I.open(0, 4))

        assert not I.closed(0, 2).adjacent(I.closed(0, 2))
        assert not I.open(0, 2).adjacent(I.open(0, 2))
        assert not I.openclosed(0, 2).adjacent(I.openclosed(0, 2))
        assert not I.closedopen(0, 2).adjacent(I.closedopen(0, 2))

    def test_same_bounds(self):
        assert not I.closed(0, 2).adjacent(I.open(0, 2))
        assert not I.open(0, 2).adjacent(I.closed(0, 2))
        assert not I.openclosed(0, 2).adjacent(I.closedopen(0, 2))
        assert not I.closedopen(0, 2).adjacent(I.openclosed(0, 2))

    def test_nonatomic_interval(self):
        assert (I.closed(0, 1) | I.closed(2, 3)).adjacent(I.open(1, 2))
        assert I.open(1, 2).adjacent(I.closed(0, 1) | I.closed(2, 3))
        assert not (I.closed(0, 1) | I.closed(2, 3)).adjacent(I.closed(1, 2))
        assert (I.closedopen(0, 1) | I.openclosed(2, 3)).adjacent(I.open(-1, 0) | I.closed(1, 2) | I.openclosed(3, 4))


class TestIntervalOverlaps():
    def test_overlaps(self):
        assert I.closed(1, 2).overlaps(I.closed(2, 3))
        assert I.closed(1, 2).overlaps(I.closedopen(2, 3))
        assert I.openclosed(1, 2).overlaps(I.closed(2, 3))
        assert I.openclosed(1, 2).overlaps(I.closedopen(2, 3))

    def test_overlaps_with_nonoverlaping(self):
        assert not I.closed(0, 1).overlaps(I.closed(3, 4))
        assert not I.closed(3, 4).overlaps(I.closed(0, 1))

    def test_overlaps_with_edge_cases(self):
        assert not I.closed(0, 1).overlaps(I.open(1, 2))
        assert not I.closed(0, 1).overlaps(I.openclosed(1, 2))
        assert not I.closedopen(0, 1).overlaps(I.closed(1, 2))
        assert not I.closedopen(0, 1).overlaps(I.closedopen(1, 2))
        assert not I.closedopen(0, 1).overlaps(I.openclosed(1, 2))
        assert not I.closedopen(0, 1).overlaps(I.open(1, 2))
        assert not I.open(0, 1).overlaps(I.open(1, 2))
        assert I.open(0, 2).overlaps(I.open(0, 1))
        assert I.open(0, 1).overlaps(I.open(0, 2))

    def test_overlaps_with_empty(self):
        assert not I.empty().overlaps(I.open(-I.inf, I.inf))
        assert not I.open(-I.inf, I.inf).overlaps(I.empty())

    def test_overlaps_with_itself(self):
        assert I.closed(0, 1).overlaps(I.closed(0, 1))
        assert I.closed(0, 1).overlaps(I.open(0, 1))
        assert I.open(0, 1).overlaps(I.closed(0, 1))
        assert I.closed(0, 1).overlaps(I.openclosed(0, 1))
        assert I.closed(0, 1).overlaps(I.closedopen(0, 1))

    def test_overlaps_with_incompatible_types(self):
        with pytest.raises(TypeError):
            I.closed(0, 1).overlaps(1)


class TestIntervalComparison:
    @pytest.mark.parametrize('i1,i2,i3', [
        (I.closed(0, 1), I.closed(1, 2), I.closed(2, 3)),
        (I.open(0, 2), I.open(1, 3), I.open(2, 4)),
    ])
    def test_equalities(self, i1, i2, i3):
        assert i1 == i1
        assert i1 != i2 and i2 != i1
        assert i1 != i3 and i3 != i1
        assert i2 != i3 and i3 != i2

        assert not i1 == 1

    @pytest.mark.parametrize('i1,i2,i3', [
        (I.closed(0, 1), I.closed(1, 2), I.closed(2, 3)),
        (I.open(0, 2), I.open(1, 3), I.open(2, 4)),
    ])
    def test_inequalities(self, i1, i2, i3):
        assert i1 < i3 and i3 > i1
        assert i1 <= i2 and i2 >= i1
        assert i1 <= i3 and i3 >= i1
        assert not i1 < i2 and not i2 > i1

    def test_closed_atomic_with_values(self):
        i = I.closed(0, 5)

        assert -1 < i
        assert -1 <= i
        assert 6 > i
        assert 6 >= i

        assert not (2 < i)
        assert 2 <= i
        assert not (5 < i)
        assert 5 <= i

        assert not (3 > i)
        assert 3 >= i
        assert not (0 > i)
        assert 0 >= i

    def test_open_atomic_with_values(self):
        i = I.open(0, 5)

        assert -1 < i
        assert -1 <= i
        assert 6 > i
        assert 6 >= i

        assert not (2 < i)
        assert 2 <= i
        assert not (5 < i)
        assert not (5 <= i)

        assert not (3 > i)
        assert 3 >= i
        assert not (0 > i)
        assert not (0 >= i)

    def test_atomic_with_infinities(self):
        i = I.closed(0, 5)
        assert -I.inf < i
        assert -I.inf <= i
        assert not (-I.inf > i)
        assert not (-I.inf >= i)

        assert I.inf > i
        assert I.inf >= i
        assert not (I.inf < i)
        assert not (I.inf <= i)

        i = I.open(0, 5)
        assert -I.inf < i
        assert -I.inf <= i
        assert not (-I.inf > i)
        assert not (-I.inf >= i)

        assert I.inf > i
        assert I.inf >= i
        assert not (I.inf < i)
        assert not (I.inf <= i)

    def test_with_values(self):
        i = I.closedopen(0, 10)

        assert -1 < i
        assert -1 <= i
        assert not (0 < i)
        assert 0 <= i
        assert not (5 < i)
        assert 5 <= i
        assert not (10 < i)
        assert not (10 <= i)
        assert not (12 < i)
        assert not (12 <= i)

        assert 12 > i
        assert 12 >= i
        assert 10 > i
        assert 10 >= i
        assert not (8 > i)
        assert 8 >= i
        assert not (0 > i)
        assert 0 >= i
        assert not (-1 > i)
        assert not (-1 >= i)

    def test_with_infinities(self):
        i = I.closedopen(0, 10)

        assert -I.inf < i
        assert -I.inf <= i
        assert not (-I.inf > i)
        assert not (-I.inf >= i)

        assert I.inf > i
        assert I.inf >= i
        assert not (I.inf < i)
        assert not (I.inf <= i)

    def test_with_intervals(self):
        i1, i2, i3 = I.closed(0, 1), I.closed(1, 2), I.closed(2, 3)

        i4 = i1 | i3

        assert i4 != i2 and i2 != i4
        assert not i4 < i2 and not i2 > i4
        assert not i4 > i2 and not i2 < i4
        assert not i4 <= i2
        assert not i4 >= i2
        assert i2 <= i4
        assert i2 >= i4

        i5 = I.closed(5, 6) | I.closed(7, 8)

        assert i4 != i5 and i5 != i4
        assert i4 < i5 and i5 > i4
        assert not i4 > i5 and not i5 < i4
        assert i4 <= i5
        assert i5 >= i4
        assert not i4 >= i5
        assert not i5 <= i4

    def test_with_empty(self):
        assert I.empty() < I.empty()
        assert I.empty() <= I.empty()
        assert I.empty() > I.empty()
        assert I.empty() >= I.empty()

        assert I.empty() < I.closed(2, 3)
        assert I.empty() <= I.closed(2, 3)
        assert I.empty() > I.closed(2, 3)
        assert I.empty() >= I.closed(2, 3)


class TestIntervalContainment:
    def test_with_values(self):
        assert 1 in I.closed(0, 2)
        assert 1 in I.closed(1, 2)
        assert 1 in I.closed(0, 1)

        assert 1 in I.open(0, 2)
        assert 1 not in I.open(0, 1)
        assert 1 not in I.open(1, 2)

    def test_with_infinities(self):
        assert 1 in I.closed(-I.inf, I.inf)
        assert 1 in I.closed(-I.inf, 1)
        assert 1 in I.closed(1, I.inf)
        assert 1 not in I.closed(-I.inf, 0)
        assert 1 not in I.closed(2, I.inf)

        assert I.inf not in I.closed(-I.inf, I.inf)
        assert -I.inf not in I.closed(-I.inf, I.inf)

    def test_with_empty(self):
        assert 1 not in I.empty()
        assert I.inf not in I.empty()
        assert -I.inf not in I.empty()

    def test_with_intervals(self):
        assert I.closed(1, 2) in I.closed(0, 3)
        assert I.closed(1, 2) in I.closed(1, 2)
        assert I.open(1, 2) in I.closed(1, 2)
        assert I.closed(1, 2) not in I.open(1, 2)
        assert I.closed(0, 1) not in I.closed(1, 2)
        assert I.closed(0, 2) not in I.closed(1, 3)
        assert I.closed(-I.inf, I.inf) in I.closed(-I.inf, I.inf)
        assert I.closed(0, 1) in I.closed(-I.inf, I.inf)
        assert I.closed(-I.inf, I.inf) not in I.closed(0, 1)

    def test_with_unions(self):
        assert I.closed(0, 1) | I.closed(2, 3) in I.closed(0, 4)
        assert I.closed(0, 1) | I.closed(2, 3) in I.closed(0, 1) | I.closed(2, 3)
        assert I.closed(0, 1) | I.closed(2, 3) in I.closed(0, 0) | I.closed(0, 1) | I.closed(2, 3)

        assert I.closed(0, 1) | I.closed(2, 3) not in I.closed(0, 2)
        assert I.closed(0, 1) | I.closed(2, 3) not in I.closed(0, 1) | I.closedopen(2, 3)

    def test_with_empty_intervals(self):
        assert I.empty() in I.closed(0, 3)
        assert I.empty() in I.empty()
        assert I.closed(0, 0) not in I.empty()

    def test_proxy_method(self):
        i1, i2 = I.closed(0, 1), I.closed(2, 3)
        assert (1 in i1) == i1.contains(1)
        assert (i1 in i2) == i2.contains(i1)


class TestIntervalIntersection:
    def test_with_itself(self):
        assert I.closed(0, 1) & I.closed(0, 1) == I.closed(0, 1)
        assert I.closed(0, 1) & I.open(0, 1) == I.open(0, 1)
        assert I.openclosed(0, 1) & I.closedopen(0, 1) == I.open(0, 1)

    def test_with_adjacent(self):
        assert I.closed(0, 2) & I.closed(2, 4) == I.singleton(2)
        assert I.open(0, 2) & I.open(2, 4) == I.empty()

    def test_with_containment(self):
        assert I.closed(0, 4) & I.closed(2, 3) == I.closed(2, 3)
        assert I.closed(0, 4) & I.closed(0, 3) == I.closed(0, 3)
        assert I.closed(0, 4) & I.open(2, 3) == I.open(2, 3)
        assert I.open(0, 4) & I.closed(2, 3) == I.closed(2, 3)
        assert I.open(0, 4) & I.closed(3, 4) == I.closedopen(3, 4)

    def test_with_overlap(self):
        assert I.closed(0, 3) & I.closed(2, 4) == I.closed(2, 3)
        assert I.open(0, 3) & I.closed(2, 4) == I.closedopen(2, 3)

    def test_empty(self):
        assert (I.closed(0, 1) & I.closed(2, 3)).empty
        assert I.closed(0, 1) & I.empty() == I.empty()

    def test_proxy_method(self):
        i1, i2 = I.closed(0, 1), I.closed(2, 3)
        assert i1 & i2 == i1.intersection(i2)

    def test_with_invalid_type(self):
        with pytest.raises(TypeError):
            I.closed(0, 1) & 1


class TestIntervalUnion:
    def test_atomic(self):
        assert I.closed(1, 2) | I.closed(1, 2) == I.closed(1, 2)
        assert I.closed(1, 4) | I.closed(2, 3) == I.closed(1, 4)
        assert I.closed(1, 2) | I.closed(2, 3) == I.closed(2, 3) | I.closed(1, 2)
        assert I.closed(1, 2) | I.closed(3, 4) == I.closed(1, 2) | I.closed(3, 4)

    def test_with_itself(self):
        assert I.closed(1, 2) | I.closed(1, 2) == I.closed(1, 2)
        assert I.open(1, 2) | I.closed(1, 2) == I.closed(1, 2)
        assert I.closedopen(1, 2) | I.openclosed(1, 2) == I.closed(1, 2)

    def test_with_containment(self):
        assert I.closed(1, 4) | I.closed(2, 3) == I.closed(1, 4)
        assert I.open(1, 4) | I.closed(2, 3) == I.open(1, 4)

    def test_with_overlap(self):
        assert I.closed(1, 3) | I.closed(2, 4) == I.closed(1, 4)

    def test_with_adjacent(self):
        assert I.closed(1, 2) | I.closed(2, 3) == I.closed(1, 3)
        assert I.closed(1, 2) | I.open(2, 3) == I.closedopen(1, 3)
        assert I.open(1, 2) | I.closed(2, 3) == I.openclosed(1, 3)
        assert I.open(1, 3) | I.open(2, 4) == I.open(1, 4)
        assert I.closedopen(1, 2) | I.closed(2, 3) == I.closed(1, 3)
        assert I.open(1, 2) | I.closed(2, 4) == I.openclosed(1, 4)

    def test_with_disjoint(self):
        assert I.closed(1, 2) | I.closed(3, 4) != I.closed(1, 4)
        assert (I.closed(1, 2) | I.closed(3, 4) | I.closed(2, 3)).atomic
        assert I.closed(1, 2) | I.closed(3, 4) | I.closed(2, 3) == I.closed(1, 4)
        assert I.closed(1, 2) | I.closed(0, 4) == I.closed(0, 4)

        assert (I.closed(0, 1) | I.closed(2, 3) | I.closed(1, 2)).atomic
        assert I.closed(0, 1) | I.closed(2, 3) | I.closed(1, 2) == I.closed(0, 3)

    def test_with_empty(self):
        assert I.closed(0, 1) | I.empty() == I.closed(0, 1)

    def test_issue_12(self):
        # https://github.com/AlexandreDecan/python-intervals/issues/12
        assert I.open(0, 2) | I.closed(0, 2) == I.closed(0, 2)
        assert I.open(0, 2) | I.closed(1, 2) == I.openclosed(0, 2)
        assert I.open(0, 2) | I.closed(0, 1) == I.closedopen(0, 2)

        assert I.closed(0, 2) | I.open(0, 2) == I.closed(0, 2)
        assert I.closed(1, 2) | I.open(0, 2) == I.openclosed(0, 2)
        assert I.closed(0, 1) | I.open(0, 2) == I.closedopen(0, 2)

        assert I.closed(0, 2) | I.singleton(2) == I.closed(0, 2)
        assert I.closedopen(0, 2) | I.singleton(2) == I.closed(0, 2)
        assert I.openclosed(0, 2) | I.singleton(2) == I.openclosed(0, 2)
        assert I.openclosed(0, 2) | I.singleton(0) == I.closed(0, 2)

        assert I.singleton(2) | I.closed(0, 2) == I.closed(0, 2)
        assert I.singleton(2) | I.closedopen(0, 2) == I.closed(0, 2)
        assert I.singleton(2) | I.openclosed(0, 2) == I.openclosed(0, 2)
        assert I.singleton(0) | I.openclosed(0, 2) == I.closed(0, 2)

    def test_issue_13(self):
        # https://github.com/AlexandreDecan/python-intervals/issues/13
        assert I.closed(1, 1) | I.openclosed(1, 2) == I.closed(1, 2)
        assert I.openclosed(1, 2) | I.closed(1, 1) == I.closed(1, 2)
        assert I.closed(0, 1) | I.openclosed(1, 2) == I.closed(0, 2)
        assert I.openclosed(1, 2) | I.closed(0, 1) == I.closed(0, 2)

        assert I.openclosed(1, 2) | I.closed(1, 1) == I.closed(1, 2)
        assert I.closed(1, 1) | I.openclosed(1, 2) == I.closed(1, 2)
        assert I.openclosed(1, 2) | I.closed(0, 1) == I.closed(0, 2)
        assert I.closed(0, 1) | I.openclosed(1, 2) == I.closed(0, 2)

    def test_proxy_method(self):
        i1, i2 = I.closed(0, 1), I.closed(2, 3)
        assert i1 | i2 == i1.union(i2)

    def test_with_invalid_type(self):
        with pytest.raises(TypeError):
            I.closed(0, 1) | 1


class TestIntervalComplement:
    def test_singleton(self):
        assert ~I.singleton(0) == I.open(-I.inf, 0) | I.open(0, I.inf)
        assert ~(I.open(-I.inf, 0) | I.open(0, I.inf)) == I.singleton(0)

    def test_nonempty(self):
        assert ~I.closed(1, 2) == I.open(-I.inf, 1) | I.open(2, I.inf)
        assert ~I.open(1, 2) == I.openclosed(-I.inf, 1) | I.closedopen(2, I.inf)

    def test_union(self):
        assert ~(I.singleton(0) | I.singleton(5) | I.singleton(10)) == I.open(-I.inf, 0) | I.open(0, 5) | I.open(5, 10) | I.open(10, I.inf)
        assert ~(I.open(0, 1) | I.closed(2, 3) | I.open(4, 5)) == I.openclosed(-I.inf, 0) | I.closedopen(1, 2) | I.openclosed(3, 4) | I.closedopen(5, I.inf)

    @pytest.mark.parametrize('i', [I.closed(0, 1), I.open(0, 1), I.openclosed(0, 1), I.closedopen(0, 1)])
    def test_identity(self, i):
        for interval in i:
            assert ~(~interval) == interval

    def test_empty(self):
        assert ~I.open(1, 1) == I.open(-I.inf, I.inf)
        assert (~I.closed(-I.inf, I.inf)).empty
        assert ~I.empty() == I.open(-I.inf, I.inf)

    def test_proxy_method(self):
        i1, i2 = I.closed(0, 1), I.closed(2, 3)
        assert ~i1 == i1.complement()
        assert ~i2 == i2.complement()


class TestIntervalDifference:
    @pytest.mark.parametrize('i', [I.closed(0, 1), I.open(0, 1), I.openclosed(0, 1), I.closedopen(0, 1), I.empty(), I.singleton(0)])
    def test_with_itself(self, i):
        assert i - i == I.empty()

    def test_with_disjoint(self):
        assert I.closed(0, 1) - I.closed(2, 3) == I.closed(0, 1)
        assert I.closed(0, 4) - I.empty() == I.closed(0, 4)
        assert I.empty() - I.closed(0, 4) == I.empty()

    def test_with_smaller(self):
        assert I.closed(0, 4) - I.closed(2, 3) == I.closedopen(0, 2) | I.openclosed(3, 4)
        assert I.closed(1, 4) - I.closed(1, 3) == I.openclosed(3, 4)
        assert I.closed(1, 4) - I.closed(2, 4) == I.closedopen(1, 2)
        assert I.closed(0, 4) - I.open(1, 2) == I.closed(0, 1) | I.closed(2, 4)
        assert I.closed(0, 2) - I.open(0, 2) == I.singleton(0) | I.singleton(2)

    def test_with_larger(self):
        assert I.closed(0, 2) - I.closed(0, 4) == I.empty()
        assert I.closed(0, 2) - I.closed(-2, 2) == I.empty()
        assert I.closed(0, 2) - I.closed(-2, 4) == I.empty()
        assert I.open(0, 2) - I.closed(0, 2) == I.empty()

    def test_with_overlap(self):
        assert I.closed(0, 2) - I.closed(1, 3) == I.closedopen(0, 1)
        assert I.closed(0, 2) - I.open(1, 3) == I.closed(0, 1)
        assert I.closed(0, 2) - I.closed(-2, 1) == I.openclosed(1, 2)
        assert I.closed(0, 2) - I.open(-2, 1) == I.closed(1, 2)

    def test_proxy_method(self):
        i1, i2 = I.closed(0, 1), I.closed(2, 3)
        assert i1 - i2 == i1.difference(i2)

    def test_with_invalid_type(self):
        with pytest.raises(TypeError):
            I.closed(0, 1) - 1


class TestIntervalIteration:
    def test_length(self):
        i1 = I.closed(10, 10) | I.closed(5, 6) | I.closed(7, 8) | I.closed(8, 9)
        assert len(i1) == 3

    def test_containment(self):
        i1 = I.closed(10, 10) | I.closed(5, 6) | I.closed(7, 8) | I.closed(8, 9)
        for i in i1:
            assert i in i1

    def test_order(self):
        i1 = I.closed(10, 10) | I.closed(5, 6) | I.closed(7, 8) | I.closed(8, 9)
        assert sorted(i1, key=lambda i: i.lower) == list(i1)
        assert sorted(i1, key=lambda i: i.upper) == list(i1)

    def test_indexes(self):
        i1 = I.closed(10, 10) | I.closed(5, 6) | I.closed(7, 8) | I.closed(8, 9)
        assert i1[0] == I.closed(5, 6)
        assert i1[1] == I.closed(7, 9)
        assert i1[2] == I.closed(10, 10)
        assert i1[-1] == I.closed(10, 10)

    def test_slices(self):
        items = [I.closed(5, 6), I.closed(7, 9), I.singleton(10)]
        interval = Interval(*items)
        assert interval[:] == items
        assert interval[:2] == items[:2]
        assert interval[::-1] == items[::-1]
        assert interval[::2] == items[::2]

    def test_missing_index(self):
        i1 = I.closed(10, 10) | I.closed(5, 6) | I.closed(7, 8) | I.closed(8, 9)
        with pytest.raises(IndexError):
            i1[3]

    def test_empty(self):
        assert len(I.empty()) == 1
        assert list(I.empty()) == [I.empty()]
        assert I.empty()[0] == I.empty()
