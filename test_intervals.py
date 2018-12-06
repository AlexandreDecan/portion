import doctest
import intervals as I
import pytest
import sys


def test_infinity_comparisons():
    assert I.inf > -I.inf
    assert -I.inf < I.inf
    assert -I.inf != I.inf
    assert not (-I.inf == I.inf)


@pytest.mark.parametrize('inf', [I.inf, -I.inf])
def test_infinity_comparisons_with_self(inf):
    assert inf == inf
    assert inf >= inf
    assert inf <= inf
    assert not (inf > inf)
    assert not (inf < inf)
    assert not (inf != inf)


@pytest.mark.parametrize('o', [0, 1, 1.0, 'a', list(), tuple(), dict(), I.closed(0, 1)])
def test_infinity_comparisons_with_objects(o):
    assert o != I.inf and not (o == I.inf)
    assert o < I.inf and I.inf > o
    assert o <= I.inf and I.inf >= o

    assert o != -I.inf and not (o == -I.inf)
    assert o > -I.inf and -I.inf < o
    assert o >= -I.inf and -I.inf <= o


def test_creation():
    assert I.closed(0, 1) == I.AtomicInterval(I.CLOSED, 0, 1, I.CLOSED)
    assert I.open(0, 1) == I.AtomicInterval(I.OPEN, 0, 1, I.OPEN)
    assert I.openclosed(0, 1) == I.AtomicInterval(I.OPEN, 0, 1, I.CLOSED)
    assert I.closedopen(0, 1) == I.AtomicInterval(I.CLOSED, 0, 1, I.OPEN)
    assert I.closed(-I.inf, I.inf) == I.open(-I.inf, I.inf)

    assert I.singleton(2) == I.closed(2, 2)
    assert I.Interval() == I.open(0, 0)
    assert I.empty() == I.Interval()
    assert I.closed(3, -3) == I.empty()
    assert I.openclosed(3, 3) == I.empty()

    assert I.Interval(I.closed(0, 1).to_atomic()) == I.closed(0, 1)
    assert I.Interval(I.closed(0, 1)) == I.closed(0, 1)
    assert I.Interval(I.closed(0, 1).to_atomic(), I.closed(2, 3)) == I.closed(0, 1) | I.closed(2, 3)
    assert I.Interval(I.closed(0, 1) | I.closed(2, 3)) == I.closed(0, 1) | I.closed(2, 3)

    with pytest.raises(TypeError):
        I.Interval(1)


def test_hash():
    assert hash(I.closed(0, 1).to_atomic()) is not None
    assert hash(I.closed(0, 1)) is not None
    assert hash(I.empty()) is not None

    # Even for unhashable bounds
    with pytest.raises(TypeError):
        hash(I.inf)
    with pytest.raises(TypeError):
        hash(-I.inf)

    assert hash(I.closed(-I.inf, I.inf).to_atomic()) is not None
    assert hash(I.closed(-I.inf, I.inf)) is not None


def test_to_string():
    i1, i2, i3, i4 = I.closed(0, 1), I.openclosed(0, 1), I.closedopen(0, 1), I.open(0, 1)

    assert I.to_string(i1) == '[0,1]'
    assert I.to_string(i2) == '(0,1]'
    assert I.to_string(i3) == '[0,1)'
    assert I.to_string(i4) == '(0,1)'

    assert I.to_string(I.empty()) == '()'
    assert I.to_string(I.singleton(1)) == '[1]'

    assert I.to_string(I.openclosed(-I.inf, 1)) == '(-inf,1]'
    assert I.to_string(I.closedopen(1, I.inf)) == '[1,+inf)'

    assert I.to_string(I.closed(0, 1) | I.closed(2, 3)) == '[0,1] | [2,3]'


def test_to_string_customized():
    i1, i2, i3, i4 = I.closed(0, 1), I.openclosed(0, 1), I.closedopen(0, 1), I.open(0, 1)
    params = {
        'disj': ' or ',
        'sep': '-',
        'left_open': '<!',
        'left_closed': '<',
        'right_open': '!>',
        'right_closed': '>',
        'conv': lambda s: '"{}"'.format(s),
        'pinf': '+oo',
        'ninf': '-oo',
    }

    assert I.to_string(i1, **params) == '<"0"-"1">'
    assert I.to_string(i2, **params) == '<!"0"-"1">'
    assert I.to_string(i3, **params) == '<"0"-"1"!>'
    assert I.to_string(i4, **params) == '<!"0"-"1"!>'

    assert I.to_string(I.empty(), **params) == '<!!>'
    assert I.to_string(I.singleton(1), **params) == '<"1">'

    assert I.to_string(I.openclosed(-I.inf, 1), **params) == '<!-oo-"1">'
    assert I.to_string(I.closedopen(1, I.inf), **params) == '<"1"-+oo!>'

    assert I.to_string(I.closed(0, 1) | I.closed(2, 3), **params) == '<"0"-"1"> or <"2"-"3">'


def test_from_string():
    i1, i2, i3, i4 = '[0,1]', '(0,1]', '[0,1)', '(0,1)'

    assert I.from_string(i1, int) == I.closed(0, 1)
    assert I.from_string(i2, int) == I.openclosed(0, 1)
    assert I.from_string(i3, int) == I.closedopen(0, 1)
    assert I.from_string(i4, int) == I.open(0, 1)

    assert I.from_string('()', int) == I.empty()
    assert I.from_string('[1]', int) == I.singleton(1)

    assert I.from_string('(-inf,1]', int) == I.openclosed(-I.inf, 1)
    assert I.from_string('[1,+inf)', int) == I.closedopen(1, I.inf)

    assert I.from_string('[0,1] | [2,3]', int) == I.closed(0, 1) | I.closed(2, 3)

    with pytest.raises(Exception):
        I.from_string('[1,2]', None)


def test_from_string_customized():
    i1, i2, i3, i4 = '<"0"-"1">', '<!"0"-"1">', '<"0"-"1"!>', '<!"0"-"1"!>'
    params = {
        'conv': lambda s: int(s[1:-1]),
        'disj': ' or ',
        'sep': '-',
        'left_open': '<!',
        'left_closed': '<',
        'right_open': '!>',
        'right_closed': '>',
        'pinf': r'\+oo',
        'ninf': '-oo',
    }

    assert I.from_string(i1, **params) == I.closed(0, 1)
    assert I.from_string(i2, **params) == I.openclosed(0, 1)
    assert I.from_string(i3, **params) == I.closedopen(0, 1)
    assert I.from_string(i4, **params) == I.open(0, 1)

    assert I.from_string('<!!>', **params) == I.empty()
    assert I.from_string('<"1">', **params) == I.singleton(1)

    assert I.from_string('<!-oo-"1">', **params) == I.openclosed(-I.inf, 1)
    assert I.from_string('<"1"-+oo!>', **params) == I.closedopen(1, I.inf)

    assert I.from_string('<"0"-"1"> or <"2"-"3">', **params) == I.closed(0, 1) | I.closed(2, 3)


def test_to_data():
    assert I.to_data(I.closedopen(2, 3)) == [(I.CLOSED, 2, 3, I.OPEN)]
    assert I.to_data(I.openclosed(2, I.inf)) == [(I.OPEN, 2, float('inf'), I.OPEN)]
    assert I.to_data(I.closed(-I.inf, 2)) == [(I.OPEN, float('-inf'), 2, I.CLOSED)]

    i = I.openclosed(-I.inf, 4) | I.closedopen(6, I.inf)
    assert I.to_data(i) == [(I.OPEN, float('-inf'), 4, I.CLOSED), (I.CLOSED, 6, float('inf'), I.OPEN)]
    assert I.to_data(i, conv=str, pinf='highest', ninf='lowest') == [(I.OPEN, 'lowest', '4', I.CLOSED), (I.CLOSED, '6', 'highest', I.OPEN)]


def test_from_data():
    assert I.from_data([(I.CLOSED, 2, 3, I.OPEN)]) == I.closedopen(2, 3)
    assert I.from_data([(I.OPEN, 2, float('inf'), I.OPEN)]) == I.openclosed(2, I.inf)
    assert I.from_data([(I.OPEN, float('-inf'), 2, I.CLOSED)]) == I.closed(-I.inf, 2)

    d = [(I.OPEN, float('-inf'), 4, I.CLOSED), (I.CLOSED, 6, float('inf'), I.OPEN)]
    assert I.from_data(d) == I.openclosed(-I.inf, 4) | I.closedopen(6, I.inf)

    d = [(I.OPEN, 'lowest', '4', I.CLOSED), (I.CLOSED, '6', 'highest', I.OPEN)]
    assert I.from_data(d, conv=int, pinf='highest', ninf='lowest') == I.openclosed(-I.inf, 4) | I.closedopen(6, I.inf)



def test_interval_to_atomic():
    intervals = [I.closed(0, 1), I.open(0, 1), I.openclosed(0, 1), I.closedopen(0, 1)]
    for interval in intervals:
        assert interval == I.Interval(interval.to_atomic())
        assert interval == interval.to_atomic()

    assert I.closed(0, 1) | I.closed(2, 3) != I.closed(0, 3)
    assert (I.closed(0, 1) | I.closed(2, 3)).to_atomic() == I.closed(0, 3)

    assert I.closed(0, 1).to_atomic() == I.closed(0, 1).enclosure()
    assert (I.closed(0, 1) | I.closed(2, 3)).enclosure() == I.closed(0, 3)

    assert I.empty().to_atomic() == I.AtomicInterval(False, I.inf, -I.inf, False)


def test_overlaps():
    # Overlaps should reject non supported types
    with pytest.raises(TypeError):
        I.closed(0, 1).to_atomic().overlaps(1)
    with pytest.raises(TypeError):
        I.closed(0, 1).overlaps(1)
        
    assert I.closed(0, 1).overlaps(I.closed(0, 1))
    assert I.closed(0, 1).overlaps(I.open(0, 1))
    assert I.open(0, 1).overlaps(I.closed(0, 1))
    assert I.closed(0, 1).overlaps(I.openclosed(0, 1))
    assert I.closed(0, 1).overlaps(I.closedopen(0, 1))

    assert I.closed(1, 2).overlaps(I.closed(2, 3)) 
    assert I.closed(1, 2).overlaps(I.closedopen(2, 3))
    assert I.openclosed(1, 2).overlaps(I.closed(2, 3)) 
    assert I.openclosed(1, 2).overlaps(I.closedopen(2, 3))

    assert not I.closed(0, 1).overlaps(I.closed(3, 4))
    assert not I.closed(3, 4).overlaps(I.closed(0, 1))

    assert not I.closed(0, 1).overlaps(I.open(1, 2))
    assert not I.closed(0, 1).overlaps(I.openclosed(1, 2))
    assert not I.closedopen(0, 1).overlaps(I.closed(1, 2))
    assert not I.closedopen(0, 1).overlaps(I.closedopen(1, 2))
    assert not I.closedopen(0, 1).overlaps(I.openclosed(1, 2))
    assert not I.closedopen(0, 1).overlaps(I.open(1, 2))
    assert not I.open(0, 1).overlaps(I.open(1, 2))

    assert not I.empty().overlaps(I.open(-I.inf, I.inf))
    assert not I.open(-I.inf, I.inf).overlaps(I.empty())


def test_overlaps_permissive():
    assert I.closed(0, 1).overlaps(I.closed(0, 1), permissive=True)
    assert I.closed(0, 1).overlaps(I.open(0, 1), permissive=True)
    assert I.open(0, 1).overlaps(I.closed(0, 1), permissive=True)
    assert I.closed(0, 1).overlaps(I.openclosed(0, 1), permissive=True)
    assert I.closed(0, 1).overlaps(I.closedopen(0, 1), permissive=True)

    assert I.closed(1, 2).overlaps(I.closed(2, 3), permissive=True) 
    assert I.closed(1, 2).overlaps(I.closedopen(2, 3), permissive=True)
    assert I.openclosed(1, 2).overlaps(I.closed(2, 3), permissive=True) 
    assert I.openclosed(1, 2).overlaps(I.closedopen(2, 3), permissive=True)

    assert not I.closed(0, 1).overlaps(I.closed(3, 4), permissive=True)
    assert not I.closed(3, 4).overlaps(I.closed(0, 1), permissive=True)

    assert I.closed(0, 1).overlaps(I.open(1, 2), permissive=True)
    assert I.closed(0, 1).overlaps(I.openclosed(1, 2), permissive=True)
    assert I.closedopen(0, 1).overlaps(I.closed(1, 2), permissive=True)
    assert I.closedopen(0, 1).overlaps(I.closedopen(1, 2), permissive=True)
    assert not I.closedopen(0, 1).overlaps(I.openclosed(1, 2), permissive=True)
    assert not I.closedopen(0, 1).overlaps(I.open(1, 2), permissive=True)
    assert not I.open(0, 1).overlaps(I.open(1, 2), permissive=True)

    assert not I.empty().overlaps(I.open(-I.inf, I.inf), permissive=True)
    assert not I.open(-I.inf, I.inf).overlaps(I.empty(), permissive=True)
    

def test_emptiness():
    assert I.openclosed(1, 1).is_empty()
    assert I.closedopen(1, 1).is_empty()
    assert I.open(1, 1).is_empty()
    assert not I.closed(1, 1).is_empty()
    assert I.Interval().is_empty()
    assert I.empty().is_empty()


@pytest.mark.parametrize('i1,i2,i3', [
    (I.closed(0, 1).to_atomic(), I.closed(1, 2).to_atomic(), I.closed(2, 3).to_atomic()),
    (I.open(0, 2).to_atomic(), I.open(1, 3).to_atomic(), I.open(2, 4).to_atomic()),
    (I.closed(0, 1), I.closed(1, 2), I.closed(2, 3)),
    (I.open(0, 2), I.open(1, 3), I.open(2, 4)),
    (I.closed(0, 1), I.closed(1, 2), I.closed(2, 3).to_atomic()),
    (I.open(0, 2), I.open(1, 3), I.open(2, 4).to_atomic()),
    (I.closed(0, 1).to_atomic(), I.closed(1, 2), I.closed(2, 3)),
    (I.open(0, 2).to_atomic(), I.open(1, 3), I.open(2, 4)),
])
def test_atomic_comparisons(i1, i2, i3):
    assert i1 == i1
    assert i1 != i2 and i2 != i1
    assert i1 != i3 and i3 != i1
    assert i2 != i3 and i3 != i2

    assert i1 < i3 and i3 > i1
    assert i1 <= i2 and i2 >= i1
    assert i1 <= i3 and i3 >= i1
    assert not i1 < i2 and not i2 > i1

    assert not i1 == 1


@pytest.mark.parametrize('i1', [I.closed(0, 1).to_atomic(), I.closed(0, 1)])
@pytest.mark.xfail(sys.version_info < (3, 0), reason='Python 2 does not raise TypeError for unsupported comparisons')
def test_comparisons_for_unsupported_types(i1):
    with pytest.raises(TypeError):
        i1 > 1
    with pytest.raises(TypeError):
        i1 >= 1
    with pytest.raises(TypeError):
        i1 < 1
    with pytest.raises(TypeError):
        i1 <= 1


def test_comparisons_of_unions():
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


def test_comparisons_of_empty():
    assert I.empty() < I.empty()
    assert I.empty() <= I.empty()
    assert I.empty() > I.empty()
    assert I.empty() >= I.empty()

    assert I.empty() < I.closed(2, 3)
    assert I.empty() <= I.closed(2, 3)
    assert I.empty() > I.closed(2, 3)
    assert I.empty() >= I.closed(2, 3)


def test_comparisons_mixed_intervals():
    # Bug introduced in 1.3.0, fixed in 1.5.2
    assert I.closed(1, 2).to_atomic() <= I.closed(0, 3)
    assert I.closed(1, 2) >= I.closed(0, 3).to_atomic()
    assert I.closed(1, 2) <= I.closed(0, 3).to_atomic()
    assert I.closed(1, 2).to_atomic() >= I.closed(0, 3)


def test_containment_for_values():
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

    assert 1 not in I.empty()
    assert I.inf not in I.empty()
    assert -I.inf not in I.empty()


def test_containment_for_intervals():
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

    assert I.empty() in I.closed(0, 3)
    assert I.empty() in I.empty()
    assert I.closed(0, 0) not in I.empty()


def test_containment_for_atomic_intervals():
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

    assert I.closed(0, 1) & I.empty() == I.empty()


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

    assert I.closed(0, 1) | I.empty() == I.closed(0, 1)


def test_iteration():
    i1 = I.closed(10, 10) | I.closed(5, 6) | I.closed(7, 8) | I.closed(8, 9)

    assert len(i1) == 3
    for i in i1:
        assert i in i1
    assert sorted(i1, key=lambda i: i.lower) == list(i1)
    assert sorted(i1, key=lambda i: i.upper) == list(i1)

    assert i1[0] == I.closed(5, 6)
    assert i1[1] == I.closed(7, 9)
    assert i1[2] == I.closed(10, 10)
    assert i1[-1] == I.closed(10, 10)
    with pytest.raises(IndexError):
        i1[3]

    assert len(I.empty()) == 0
    assert list(I.empty()) == []
    with pytest.raises(IndexError):
        I.empty()[0]


def test_complement():
    assert ~I.closed(1, 2) == I.open(-I.inf, 1) | I.open(2, I.inf)
    assert ~I.open(1, 2) == I.openclosed(-I.inf, 1) | I.closedopen(2, I.inf)

    intervals = [I.closed(0, 1), I.open(0, 1), I.openclosed(0, 1), I.closedopen(0, 1)]
    for interval in intervals:
        assert ~(~interval) == interval
    assert ~I.open(1, 1) == I.open(-I.inf, I.inf)
    assert (~I.closed(-I.inf, I.inf)).is_empty()

    assert ~I.empty() == I.open(-I.inf, I.inf)


def test_difference():
    assert I.closed(1, 4) - I.closed(1, 3) == I.openclosed(3, 4)
    assert I.closed(1, 4) - I.closed(1, 3).to_atomic() == I.openclosed(3, 4)
    assert I.closed(1, 4).to_atomic() - I.closed(1, 3).to_atomic() == I.openclosed(3, 4)
    assert (I.closed(1, 4) - I.closed(1, 4)).is_empty()
    assert I.closed(0, 1) - I.closed(2, 3) == I.closed(0, 1)
    assert I.closed(0, 4) - I.closed(2, 3) == I.closedopen(0, 2) | I.openclosed(3, 4)

    assert I.closed(0, 4) - I.closed(2, 3) == I.closed(0, 4).to_atomic() - I.closed(2, 3)
    assert I.closed(0, 4) - I.closed(2, 3) == I.closed(0, 4).to_atomic() - I.closed(2, 3).to_atomic()
    assert I.closed(0, 4) - I.closed(2, 3) == I.closed(0, 4) - I.closed(2, 3).to_atomic()

    assert I.closed(0, 4) - I.empty() == I.closed(0, 4)
    assert I.empty() - I.closed(0, 4) == I.empty()


def test_proxy_methods():
    i1, i2 = I.closed(0, 1), I.closed(2, 3)
    assert i1 & i2 == i1.intersection(i2)
    assert i1 | i2 == i1.union(i2)
    assert (i1 in i2) == i2.contains(i1)
    assert ~i1 == i1.complement()
    assert i1 - i2 == i1.difference(i2)

    with pytest.raises(TypeError):
        i1 & 1
    with pytest.raises(TypeError):
        i1 | 1
    with pytest.raises(TypeError):
        i1 - 1

    i1, i2 = I.closed(0, 1).to_atomic(), I.closed(2, 3).to_atomic()
    assert i1 & i2 == i1.intersection(i2)
    assert i1 | i2 == i1.union(i2)
    assert (i1 in i2) == i2.contains(i1)
    assert ~i1 == i1.complement()
    assert i1 - i2 == i1.difference(i2)

    with pytest.raises(TypeError):
        i1 & 1
    with pytest.raises(TypeError):
        i1 | 1
    with pytest.raises(TypeError):
        i1 - 1


def test_example():
    failure = None

    try:
        doctest.testfile('README.md', raise_on_error=True, globs={'I': I})
    except doctest.DocTestFailure as e:
        failure = e.example.want, e.got, e.example.source

    if failure:
        # Make pytest display it outside the "except" block, to avoid a noisy traceback
        want, got, example = failure
        assert want.strip() == got.strip(), 'DocTest failure in "{}"'.format(example.strip())
        assert False  # In case .strip() removed something useful
