import pytest
import intervals as I


def test_infinity():
    assert I.inf == I.inf
    assert I.inf >= I.inf
    assert I.inf <= I.inf
    assert not (I.inf > I.inf)
    assert not (I.inf < I.inf)
    assert not (I.inf != I.inf)

    assert -I.inf == -I.inf
    assert -I.inf >= -I.inf
    assert -I.inf <= -I.inf
    assert not (-I.inf > -I.inf)
    assert not (-I.inf < -I.inf)
    assert not (-I.inf != -I.inf)

    assert I.inf > -I.inf
    assert -I.inf < I.inf
    assert -I.inf != I.inf
    assert not (-I.inf == I.inf)


def test_creation():
    assert I.closed(0, 1) == I.AtomicInterval(I.CLOSED, 0, 1, I.CLOSED)
    assert I.open(0, 1) == I.AtomicInterval(I.OPEN, 0, 1, I.OPEN)
    assert I.openclosed(0, 1) == I.AtomicInterval(I.OPEN, 0, 1, I.CLOSED)
    assert I.closedopen(0, 1) == I.AtomicInterval(I.CLOSED, 0, 1, I.OPEN)
    assert I.closed(-I.inf, I.inf) == I.open(-I.inf, I.inf)

    with pytest.raises(ValueError):
        I.closed(1, -1)

    assert I.singleton(2) == I.closed(2, 2)
    assert I.Interval() == I.open(0, 0)


def test_to_interval_to_atomic():
    intervals = [I.closed(0, 1), I.open(0, 1), I.openclosed(0, 1), I.closedopen(0, 1)]
    for interval in intervals:
        assert interval == I.Interval(interval.to_atomic())
        assert interval == interval.to_atomic()

    assert I.closed(0, 1) | I.closed(2, 3) != I.closed(0, 3)
    assert (I.closed(0, 1) | I.closed(2, 3)).to_atomic() == I.closed(0, 3)


def test_overlaps():
    assert I.closed(0, 1).overlaps(I.closed(0, 1))
    assert I.closed(0, 1).overlaps(I.open(0, 1))
    assert I.closed(0, 1).overlaps(I.closed(1, 2))
    assert not I.closed(0, 1).overlaps(I.closed(3, 4))
    assert not I.closed(0, 1).overlaps(I.open(1, 2))

    assert I.closed(0, 1).overlaps(I.closed(0, 1), permissive=True)
    assert I.closed(0, 1).overlaps(I.open(0, 1), permissive=True)
    assert I.closed(0, 1).overlaps(I.closed(1, 2), permissive=True)
    assert not I.closed(0, 1).overlaps(I.closed(3, 4), permissive=True)
    assert I.closed(0, 1).overlaps(I.open(1, 2), permissive=True)

    # Overlaps should reject non supported types
    with pytest.raises(TypeError):
        I.closed(0, 1).to_atomic().overlaps(1)


def test_emptyness():
    assert I.openclosed(1, 1).is_empty()
    assert I.closedopen(1, 1).is_empty()
    assert I.open(1, 1).is_empty()
    assert not I.closed(1, 1).is_empty()
    assert I.Interval().is_empty()


def test_containment():
    # Values
    assert 1 in I.closed(0, 2)
    assert 1 in I.closed(1, 2)
    assert 1 in I.closed(0, 1)

    assert 1 in I.open(0, 2)
    assert 1 not in I.open(0, 1)
    assert 1 not in I.open(1, 2)

    assert 1 in I.closed(-I.inf, I.inf)
    assert 1 in I.closed(-I.inf, 1)
    assert 1 in I.closed(1, I.inf)
    assert 1 not in I.closed(-I.inf, 0)
    assert 1 not in I.closed(2, I.inf)

    # Intervals
    assert I.closed(1, 2) in I.closed(0, 3)
    assert I.closed(1, 2) in I.closed(1, 2)
    assert I.open(1, 2) in I.closed(1, 2)
    assert I.closed(1, 2) not in I.open(1, 2)
    assert I.closed(0, 1) not in I.closed(1, 2)
    assert I.closed(0, 2) not in I.closed(1, 3)
    assert I.closed(-I.inf, I.inf) in I.closed(-I.inf, I.inf)
    assert I.closed(0, 1) in I.closed(-I.inf, I.inf)
    assert I.closed(-I.inf, I.inf) not in I.closed(0, 1)

    # AtomicIntervals
    assert I.closed(1, 2) in I.closed(0, 3).to_atomic()
    assert I.closed(1, 2) in I.closed(1, 2).to_atomic()
    assert I.open(1, 2) in I.closed(1, 2).to_atomic()
    assert I.closed(1, 2) not in I.open(1, 2).to_atomic()
    assert I.closed(0, 1) not in I.closed(1, 2).to_atomic()
    assert I.closed(0, 2) not in I.closed(1, 3).to_atomic()
    assert I.closed(-I.inf, I.inf) in I.closed(-I.inf, I.inf).to_atomic()
    assert I.closed(0, 1) in I.closed(-I.inf, I.inf).to_atomic()
    assert I.closed(-I.inf, I.inf) not in I.closed(0, 1).to_atomic()


def test_intersection():
    assert I.closed(0, 1) & I.closed(0, 1) == I.closed(0, 1)
    assert I.closed(0, 1) & I.closed(0, 1).to_atomic() == I.closed(0, 1)
    assert I.closed(0, 1) & I.open(0, 1) == I.open(0, 1)
    assert I.openclosed(0, 1) & I.closedopen(0, 1) == I.open(0, 1)
    assert (I.closed(0, 1) & I.closed(2, 3)).is_empty()

    with pytest.raises(TypeError):
        I.closed(0, 1) & 1
    with pytest.raises(TypeError):
        I.closed(0, 1).to_atomic() & 1


def test_union():
    assert I.closed(1, 2).to_atomic() | I.closed(1, 2).to_atomic() == I.closed(1, 2).to_atomic()
    assert I.closed(1, 4).to_atomic() | I.closed(2, 3).to_atomic() == I.closed(1, 4).to_atomic()
    assert I.closed(1, 2).to_atomic() | I.closed(2, 3).to_atomic() == I.closed(2, 3).to_atomic() | I.closed(1, 2).to_atomic()
    assert I.closed(1, 2).to_atomic() | I.closed(3, 4).to_atomic() == I.closed(1, 2) | I.closed(3, 4)

    assert I.closed(1, 2) | I.closed(1, 2) == I.closed(1, 2)
    assert I.closed(1, 4) | I.closed(2, 3) == I.closed(2, 3) | I.closed(1, 4)
    assert I.closed(1, 4) | I.closed(2, 3) == I.closed(1, 4)
    assert I.closed(1, 4) | I.closed(2, 3).to_atomic() == I.closed(1, 4)
    assert I.closed(1, 4) | I.closed(2, 3).to_atomic() == I.closed(2, 3).to_atomic() | I.closed(1, 4)

    assert I.closed(1, 2) | I.open(2, 3) == I.closedopen(1, 3)
    assert I.closed(1, 3) | I.closed(2, 4) == I.closed(1, 4)

    assert I.closed(1, 2) | I.closed(2, 3) == I.closed(2, 3) | I.closed(1, 2)

    assert I.closedopen(1, 2) | I.closed(2, 3) == I.closed(1, 3)
    assert I.open(1, 2) | I.closed(2, 4) == I.openclosed(1, 4)

    assert I.closed(1, 2) | I.closed(3, 4) != I.closed(1, 4)
    assert (I.closed(1, 2) | I.closed(3, 4) | I.closed(2, 3)).is_atomic()
    assert I.closed(1, 2) | I.closed(3, 4) | I.closed(2, 3) == I.closed(1, 4)
    assert I.closed(1, 2) | I.closed(0, 4) == I.closed(0, 4)

    assert (I.closed(0, 1) | I.closed(2, 3) | I.closed(1, 2)).is_atomic()
    assert I.closed(0, 1) | I.closed(2, 3) | I.closed(1, 2) == I.closed(0, 3)

    with pytest.raises(TypeError):
        I.closed(0, 1) | 1
    with pytest.raises(TypeError):
        I.closed(0, 1).to_atomic() | 1


def test_complement():
    assert ~I.closed(1, 2) == I.open(-I.inf, 1) | I.open(2, I.inf)
    assert ~I.open(1, 2) == I.openclosed(-I.inf, 1) | I.closedopen(2, I.inf)

    intervals = [I.closed(0, 1), I.open(0, 1), I.openclosed(0, 1), I.closedopen(0, 1)]
    for interval in intervals:
        assert ~(~interval) == interval
    assert ~I.open(1, 1) == I.open(-I.inf, I.inf)
    assert (~I.closed(-I.inf, I.inf)).is_empty()


def test_difference():
    assert I.closed(1, 4) - I.closed(1, 3) == I.openclosed(3, 4)
    assert I.closed(1, 4) - I.closed(1, 3).to_atomic() == I.openclosed(3, 4)
    assert I.closed(1, 4).to_atomic() - I.closed(1, 3).to_atomic() == I.openclosed(3, 4)
    assert (I.closed(1, 4) - I.closed(1, 4)).is_empty()
    assert I.closed(0, 1) - I.closed(2, 3) == I.closed(0, 1)
    assert I.closed(0, 4) - I.closed(2, 3) == I.closedopen(0, 2) | I.openclosed(3, 4)

    with pytest.raises(TypeError):
        I.closed(0, 1) - 1
    with pytest.raises(TypeError):
        I.closed(0, 1).to_atomic() - 1


def test_example():
    with open('README.md', 'r') as f:
        readme = f.read()

    lines = iter([e.strip() for e in readme.splitlines()])
    for line in lines:
        if line.startswith('>>>'):
            assert repr(eval(line.replace('>>> ', ''))) == next(lines), line
