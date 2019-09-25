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


@pytest.mark.skipif(sys.version_info < (3,0), reason='Not supported in Python 2')
def test_infinities_are_singletons():
    assert I._PInf() == I._PInf()
    assert I._PInf() is I._PInf()
    assert I._PInf() is -I._NInf()

    assert I._NInf() == I._NInf()
    assert I._NInf() is I._NInf()

    assert I._PInf() is not I._NInf()
    assert I._PInf() is not -I._PInf()


@pytest.mark.parametrize('o', [0, 1, 1.0, 'a', list(), tuple(), dict()])
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

    # I.empty() is a singleton
    assert I.empty() is I.empty()

    assert I.Interval(I.closed(0, 1).to_atomic()) == I.closed(0, 1)
    assert I.Interval(I.closed(0, 1)) == I.closed(0, 1)
    assert I.Interval(I.closed(0, 1).to_atomic(), I.closed(2, 3)) == I.closed(0, 1) | I.closed(2, 3)
    assert I.Interval(I.closed(0, 1) | I.closed(2, 3)) == I.closed(0, 1) | I.closed(2, 3)

    with pytest.raises(TypeError):
        I.Interval(1)


def test_atomic_bounds():
    i = I.openclosed(1, 2).to_atomic()
    assert i.left == I.OPEN
    assert i.right == I.CLOSED
    assert i.lower == 1
    assert i.upper == 2

    i = I.openclosed(10, -10).to_atomic()
    assert i.left == I.OPEN
    assert i.right == I.OPEN
    assert i.lower == I.inf
    assert i.upper == -I.inf


def test_bounds():
    i = I.openclosed(1, 2)
    assert i.left == I.OPEN
    assert i.right == I.CLOSED
    assert i.lower == 1
    assert i.upper == 2

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

    assert I.to_data(I.empty()) == [(I.OPEN, float('inf'), float('-inf'), I.OPEN)]

    i = I.openclosed(-I.inf, 4) | I.closedopen(6, I.inf)
    assert I.to_data(i) == [(I.OPEN, float('-inf'), 4, I.CLOSED), (I.CLOSED, 6, float('inf'), I.OPEN)]
    assert I.to_data(i, conv=str, pinf='highest', ninf='lowest') == [(I.OPEN, 'lowest', '4', I.CLOSED), (I.CLOSED, '6', 'highest', I.OPEN)]


def test_from_data():
    assert I.from_data([(I.CLOSED, 2, 3, I.OPEN)]) == I.closedopen(2, 3)
    assert I.from_data([(I.OPEN, 2, float('inf'), I.OPEN)]) == I.openclosed(2, I.inf)
    assert I.from_data([(I.OPEN, float('-inf'), 2, I.CLOSED)]) == I.closed(-I.inf, 2)

    assert I.from_data([]) == I.empty()

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


def test_replace_atomic():
    i = I.closed(0, 1).to_atomic()
    assert i.replace() == i
    assert i.replace(I.OPEN, 2, 3, I.OPEN) == I.open(2, 3)
    assert i.replace(upper=2, left=I.OPEN) == I.openclosed(0, 2)

    assert i.replace(lower=lambda v: 1 + v) == I.singleton(1)
    assert i.replace(left=lambda v: not v, right=lambda v: not v) == I.open(0, 1)

    assert I.empty().to_atomic().replace(left=I.CLOSED, right=I.CLOSED) == I.empty()
    assert I.empty().to_atomic().replace(lower=1, upper=2) == I.open(1, 2)
    assert I.empty().to_atomic().replace(lower=lambda v: 1, upper=lambda v: 2) == I.empty()
    assert I.empty().to_atomic().replace(lower=lambda v: 1, upper=lambda v: 2, ignore_inf=False) == I.open(1, 2)


def test_replace():
    i = I.open(-I.inf, I.inf)
    assert i.replace(lower=lambda v: 1, upper=lambda v: 1) == I.open(-I.inf, I.inf)
    assert i.replace(lower=lambda v: 1, upper=lambda v: 2, ignore_inf=False) == I.open(1, 2)

    assert I.empty().replace(left=I.CLOSED, right=I.CLOSED) == I.empty()
    assert I.empty().replace(lower=1, upper=2) == I.open(1, 2)
    assert I.empty().replace(lower=lambda v: 1, upper=lambda v: 2) == I.empty()
    assert I.empty().replace(lower=lambda v: 1, upper=lambda v: 2, ignore_inf=False) == I.open(1, 2)

    i = I.closed(0, 1) | I.open(2, 3)
    assert i.replace() == i
    assert i.replace(I.OPEN, -1, 4, I.OPEN) == I.openclosed(-1, 1) | I.open(2, 4)
    assert i.replace(lower=2) == I.closedopen(2, 3)
    assert i.replace(upper=1) == I.closedopen(0, 1)
    assert i.replace(lower=5) == I.empty()
    assert i.replace(upper=-5) == I.empty()
    assert i.replace(left=lambda v: not v, lower=lambda v: v - 1, upper=lambda v: v + 1, right=lambda v: not v) == I.openclosed(-1, 1) | I.openclosed(2, 4)

    assert I.empty().replace(lower=2, upper=4) == I.open(2, 4)


def test_apply():
    i = I.closed(0, 1)
    assert i.apply(lambda s: s) == i
    assert i.apply(lambda s: (False, -1, 2, False)) == I.open(-1, 2)
    assert i.apply(lambda s: I.AtomicInterval(False, -1, 2, False)) == I.open(-1, 2)
    assert i.apply(lambda s: I.open(-1, 2)) == I.open(-1, 2)

    i = I.closed(0, 1) | I.closed(2, 3)
    assert i.apply(lambda s: s) == i
    assert i.apply(lambda s: (False, -1, 2, False)) == I.open(-1, 2)
    assert i.apply(lambda s: (not s.left, s.lower - 1, s.upper - 1, not s.right)) == I.open(-1, 0) | I.open(1, 2)
    assert i.apply(lambda s: I.AtomicInterval(False, -1, 2, False)) == I.open(-1, 2)
    assert i.apply(lambda s: I.open(-1, 2)) == I.open(-1, 2)

    assert i.apply(lambda s: (s.left, s.lower, s.upper * 2, s.right)) == I.closed(0, 6)

    assert I.empty().apply(lambda s: (I.CLOSED, 1, 2, I.CLOSED)) == I.closed(1, 2)

    with pytest.raises(TypeError):
        i.apply(lambda s: None)

    with pytest.raises(TypeError):
        i.apply(lambda s: 'unsupported')


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

    # https://github.com/AlexandreDecan/python-intervals/issues/13
    assert not I.closed(0, 1).overlaps(I.openclosed(1, 2))
    assert not I.closedopen(0, 1).overlaps(I.closed(1, 2))
    assert not I.closed(1, 1).overlaps(I.openclosed(1, 2))
    assert not I.closedopen(1, 1).overlaps(I.closed(1, 2))
    assert not I.openclosed(1, 2).overlaps(I.closed(0, 1))
    assert not I.openclosed(1, 2).overlaps(I.closed(1, 1))

    assert I.open(0, 2).overlaps(I.open(0, 1))
    assert I.open(0, 1).overlaps(I.open(0, 2))


def test_overlaps_adjacent():
    # Check warnings for "permissive"
    with pytest.warns(DeprecationWarning, match='permissive'):
        I.closed(0, 1).to_atomic().overlaps(I.open(3, 4).to_atomic(), permissive=True)
    with pytest.warns(DeprecationWarning, match='permissive'):
        I.closed(0, 1).overlaps(I.open(3, 4), permissive=True)

    assert I.closed(0, 1).overlaps(I.closed(0, 1), adjacent=True)
    assert I.closed(0, 1).overlaps(I.open(0, 1), adjacent=True)
    assert I.open(0, 1).overlaps(I.closed(0, 1), adjacent=True)
    assert I.closed(0, 1).overlaps(I.openclosed(0, 1), adjacent=True)
    assert I.closed(0, 1).overlaps(I.closedopen(0, 1), adjacent=True)

    assert I.closed(1, 2).overlaps(I.closed(2, 3), adjacent=True)
    assert I.closed(1, 2).overlaps(I.closedopen(2, 3), adjacent=True)
    assert I.openclosed(1, 2).overlaps(I.closed(2, 3), adjacent=True)
    assert I.openclosed(1, 2).overlaps(I.closedopen(2, 3), adjacent=True)

    assert not I.closed(0, 1).overlaps(I.closed(3, 4), adjacent=True)
    assert not I.closed(3, 4).overlaps(I.closed(0, 1), adjacent=True)

    assert I.closed(0, 1).overlaps(I.open(1, 2), adjacent=True)
    assert I.closed(0, 1).overlaps(I.openclosed(1, 2), adjacent=True)
    assert I.closedopen(0, 1).overlaps(I.closed(1, 2), adjacent=True)
    assert I.closedopen(0, 1).overlaps(I.closedopen(1, 2), adjacent=True)
    assert not I.closedopen(0, 1).overlaps(I.openclosed(1, 2), adjacent=True)
    assert not I.closedopen(0, 1).overlaps(I.open(1, 2), adjacent=True)
    assert not I.open(0, 1).overlaps(I.open(1, 2), adjacent=True)

    assert not I.empty().overlaps(I.open(-I.inf, I.inf), adjacent=True)
    assert not I.open(-I.inf, I.inf).overlaps(I.empty(), adjacent=True)

    # https://github.com/AlexandreDecan/python-intervals/issues/13
    assert I.closed(0, 1).overlaps(I.openclosed(1, 2), adjacent=True)
    assert I.closedopen(0, 1).overlaps(I.closed(1, 2), adjacent=True)
    assert I.closed(1, 1).overlaps(I.openclosed(1, 2), adjacent=True)
    assert I.openclosed(1, 2).overlaps(I.closed(0, 1), adjacent=True)
    assert I.openclosed(1, 2).overlaps(I.closed(1, 1), adjacent=True)


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


def test_comparisons_with_value_1():
    i = I.closed(0, 5).to_atomic()

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

    i = I.open(0, 5).to_atomic()

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

    assert -I.inf < i
    assert -I.inf <= i
    assert not (-I.inf > i)
    assert not (-I.inf >= i)

    assert I.inf > i
    assert I.inf >= i
    assert not (I.inf < i)
    assert not (I.inf <= i)


@pytest.mark.parametrize('i', [I.closedopen(0, 10).to_atomic(), I.closedopen(0, 10)])
def test_comparisons_with_value_2(i):
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

    assert -I.inf < i
    assert -I.inf <= i
    assert not (-I.inf > i)
    assert not (-I.inf >= i)

    assert I.inf > i
    assert I.inf >= i
    assert not (I.inf < i)
    assert not (I.inf <= i)


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

    # https://github.com/AlexandreDecan/python-intervals/issues/13
    assert I.closed(1, 1) | I.openclosed(1, 2) == I.closed(1, 2)
    assert I.openclosed(1, 2) | I.closed(1, 1) == I.closed(1, 2)
    assert I.closed(0, 1) | I.openclosed(1, 2) == I.closed(0, 2)
    assert I.openclosed(1, 2) | I.closed(0, 1) == I.closed(0, 2)

    assert I.openclosed(1, 2) | I.closed(1, 1) == I.closed(1, 2)
    assert I.closed(1, 1) | I.openclosed(1, 2) == I.closed(1, 2)
    assert I.openclosed(1, 2) | I.closed(0, 1) == I.closed(0, 2)
    assert I.closed(0, 1) | I.openclosed(1, 2) == I.closed(0, 2)


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

    assert len(I.empty()) == 1
    assert list(I.empty()) == [I.empty().to_atomic()]
    assert I.empty()[0] == I.empty().to_atomic()


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


def test_iterate():
    # Default parameters
    assert list(I.iterate(I.closed(0, 2), incr=1)) == [0, 1, 2]
    assert list(I.iterate(I.closedopen(0, 2), incr=1)) == [0, 1]
    assert list(I.iterate(I.openclosed(0, 2), incr=1)) == [1, 2]
    assert list(I.iterate(I.open(0, 2), incr=1)) == [1]
    assert list(I.iterate(I.open(0, 2.5), incr=1)) == [1, 2]

    # Empty intervals or iterations
    assert list(I.iterate(I.empty(), incr=1)) == []
    assert list(I.iterate(I.open(0, 1), incr=1)) == []

    # Infinities
    with pytest.raises(ValueError):
        list(I.iterate(I.openclosed(-I.inf, 2), incr=1))
    gen = I.iterate(I.closedopen(0, I.inf), incr=1)
    assert next(gen) == 0
    assert next(gen) == 1
    assert next(gen) == 2  # and so on

    # Unions
    assert list(I.iterate(I.closed(0, 1) | I.closed(5, 6), incr=1)) == [0, 1, 5, 6]
    assert list(I.iterate(I.closed(0, 1) | I.closed(2.5, 4), incr=1)) == [0, 1, 2.5, 3.5]
    assert list(I.iterate(I.open(0, 1) | I.open(1, 2), incr=1)) == []
    assert list(I.iterate(I.open(0.5, 1) | I.open(1, 3), incr=1)) == [2]

    # Step
    assert list(I.iterate(I.closed(0, 6), incr=2)) == [0, 2, 4, 6]
    assert list(I.iterate(I.closed(0, 6), incr=4)) == [0, 4]
    assert list(I.iterate(I.closed(0, 6), incr=lambda x: x + 2)) == [0, 2, 4, 6]

    # Base
    assert list(I.iterate(I.closed(0.4, 2), incr=1, base=lambda x: round(x))) == [1, 2]
    assert list(I.iterate(I.closed(0.6, 2), incr=1, base=lambda x: round(x))) == [1, 2]

    # Reversed
    assert list(I.iterate(I.closed(0, 1), incr=1, reverse=True)) == [1, 0]
    assert list(I.iterate(I.open(0, 3), incr=1, reverse=True)) == [2, 1]
    assert list(I.iterate(I.closed(0, 1), incr=0.5, reverse=True)) == [1, 0.5, 0]
    assert list(I.iterate(I.closed(0, 2), incr=1, base=lambda x: x-1, reverse=True)) == [1, 0]

    assert list(I.iterate(I.closed(0, 2) | I.closed(4, 5), incr=1, reverse=True)) == [5, 4, 2, 1, 0]

    with pytest.raises(ValueError):
        list(I.iterate(I.closedopen(0, I.inf), incr=1, reverse=True))
    gen = I.iterate(I.openclosed(-I.inf, 2), incr=1, reverse=True)
    assert next(gen) == 2
    assert next(gen) == 1
    assert next(gen) == 0  # and so on


def test_intervaldict_get_set():
    d = I.IntervalDict()

    # Single value
    d[I.closed(0, 2)] = 0
    assert len(d) == 1
    assert d[2] == 0
    assert d.get(2) == 0
    with pytest.raises(KeyError):
        d[3]
    assert d.get(3) is None

    # Intervals
    d = I.IntervalDict([(I.closed(0, 2), 0)])
    assert d[I.open(-I.inf, I.inf)].items() == [(I.closed(0, 2), 0)]
    assert d[I.closed(0, 2)].items() == [(I.closed(0, 2), 0)]
    assert d[I.closed(-1, 0)].items() == [(I.singleton(0), 0)]
    assert d[I.closed(-2, -1)].items() == []
    assert d.get(I.closed(0, 2)).items() == [(I.closed(0, 2), 0)]
    assert d.get(I.closed(-2, -1)).items() == [(I.closed(-2, -1), None)]
    assert d.get(I.closed(-1, 0)).items() == [(I.closedopen(-1, 0), None), (I.singleton(0), 0)]

    d[I.closed(1, 3)] = 1
    assert d.items() == [(I.closedopen(0, 1), 0), (I.closed(1, 3), 1)]
    assert len(d) == 2
    assert d[0] == 0
    assert d.get(0, -1) == 0
    assert d[1] == 1
    assert d.get(1, -1) == 1
    assert d[3] == 1
    assert d.get(3, -1) == 1
    with pytest.raises(KeyError):
        d[4]
    assert d.get(4, -1) == -1

    # Set values
    d = I.IntervalDict([(I.closed(0, 2), 0)])
    d[3] = 2
    assert d.items() == [(I.closed(0, 2), 0), (I.singleton(3), 2)]
    d[3] = 3
    assert d.items() == [(I.closed(0, 2), 0), (I.singleton(3), 3)]
    d[I.closed(0, 2)] = 1
    assert d.items() == [(I.closed(0, 2), 1), (I.singleton(3), 3)]
    d[I.closed(-1, 1)] = 2
    assert d.items() == [(I.closed(-1, 1), 2), (I.openclosed(1, 2), 1), (I.singleton(3), 3)]

    d = I.IntervalDict([(I.closed(0, 2), 0)])
    d[I.closed(-1, 4)] = 1
    assert d.items() == [(I.closed(-1, 4), 1)]
    d[I.closed(5, 6)] = 1
    assert d.items() == [(I.closed(-1, 4) | I.closed(5, 6), 1)]

    # Delete
    d = I.IntervalDict([(I.closed(0, 2), 0)])
    del d[1]
    with pytest.raises(KeyError):
        d[1]
    with pytest.raises(KeyError):
        del d[3]

    d = I.IntervalDict([(I.closed(0, 2), 0)])
    del d[I.closed(-1, 1)]
    assert d.items() == [(I.openclosed(1, 2), 0)]

    del d[I.closed(-10, -9)]
    assert d.items() == [(I.openclosed(1, 2), 0)]
    del d[I.empty()]
    assert d.items() == [(I.openclosed(1, 2), 0)]

    # setdefault
    d = I.IntervalDict([(I.closed(0, 2), 0)])
    assert d.setdefault(-1, default=0) == 0
    assert d[-1] == 0
    assert d.setdefault(0, default=1) == 0
    assert d[0] == 0

    d = I.IntervalDict([(I.closed(0, 2), 0)])
    t = d.setdefault(I.closed(-2, -1), -1)
    assert t.items() == [(I.closed(-2, -1), -1)]
    assert d.items() == [(I.closed(-2, -1), -1), (I.closed(0, 2), 0)]

    d = I.IntervalDict([(I.closed(0, 2), 0)])
    t = d.setdefault(I.closed(-1, 1), 2)
    assert t.items() == [(I.closedopen(-1, 0), 2), (I.closed(0, 1), 0)]
    assert d.items() == [(I.closedopen(-1, 0), 2), (I.closed(0, 2), 0)]


def test_intervaldict_iterators():
    d = I.IntervalDict([(I.closedopen(0, 1), 0), (I.closedopen(1, 3), 1), (I.singleton(3), 2)])

    assert d.keys() == [I.closedopen(0, 1), I.closedopen(1, 3), I.singleton(3)]
    assert d.domain() == I.closed(0, 3)
    assert d.values() == [0, 1, 2]
    assert d.items() == list(zip(d.keys(), d.values()))
    assert list(d) == d.keys()

    # Iterators on empty
    assert I.IntervalDict().values() == []
    assert I.IntervalDict().items() == []
    assert I.IntervalDict().keys() == []
    assert I.IntervalDict().domain() == I.empty()


def test_intervaldict_combine():
    add = lambda x, y: x + y

    assert I.IntervalDict().combine(I.IntervalDict(), add) == I.IntervalDict()

    d = I.IntervalDict([(I.closed(0, 3), 0)])
    assert I.IntervalDict().combine(d, add) == d
    assert d.combine(I.IntervalDict(), add) == d

    d1 = I.IntervalDict([(I.closed(1, 3) | I.closed(5, 7), 1)])
    d2 = I.IntervalDict([(I.closed(2, 4) | I.closed(6, 8), 2)])
    assert d1.combine(d2, add) == d2.combine(d1, add)
    assert d1.combine(d2, add) == I.IntervalDict([
        (I.closedopen(1, 2) | I.closedopen(5, 6), 1),
        (I.closed(2, 3) | I.closed(6, 7), 3),
        (I.openclosed(3, 4) | I.openclosed(7, 8), 2),
    ])

    d1 = I.IntervalDict({
        I.closed(0, 1): 2,
        I.closed(3, 4): 2
    })
    d2 = I.IntervalDict({
        I.closed(1, 3): 3,
        I.closed(4, 5): 1
    })
    assert d1.combine(d2, add) == d2.combine(d1, add)
    assert d1.combine(d2, add) == I.IntervalDict({
        I.closedopen(0, 1): 2,
        I.singleton(1): 5,
        I.open(1, 3): 3,
        I.singleton(3): 5,
        I.open(3, 4): 2,
        I.singleton(4): 3,
        I.openclosed(4, 5): 1,
    })


def test_intervaldict_other_methods():
    # Containment
    d = I.IntervalDict([(I.closed(0, 3), 0)])
    assert 0 in d
    assert -1 not in d
    assert I.closed(-2, -1) not in d
    assert I.closed(1, 2) in d
    assert I.closed(1, 4) not in d

    # Repr
    assert repr(d) == '{' + repr(I.closed(0, 3)) + ': 0}'

    # pop
    t = d.pop(2)
    assert t == 0
    t = d.pop(4, 1)
    assert t == 1
    with pytest.raises(KeyError):
        d.pop(4)

    # pop intervals
    d = I.IntervalDict([(I.closed(0, 3), 0)])
    t = d.pop(I.closed(0, 1))
    assert t.items() == [(I.closed(0, 1), 0)]
    assert d.items() == [(I.openclosed(1, 3), 0)]
    t = d.pop(I.closed(0, 2), 1)
    assert t.items() == [(I.closed(0, 1), 1), (I.openclosed(1, 2), 0)]
    assert d.items() == [(I.openclosed(2, 3), 0)]

    # popitem
    d = I.IntervalDict([(I.closed(0, 3), 0)])
    t = d.popitem()
    assert t.items() == [(I.closed(0, 3), 0)]
    assert len(d) == 0

    with pytest.raises(KeyError):
        I.IntervalDict().popitem()

    # clear
    d = I.IntervalDict([(I.closed(0, 3), 0)])
    d.clear()
    assert d == I.IntervalDict()
    d.clear()
    assert d == I.IntervalDict()

    # copy
    d = I.IntervalDict([(I.closed(0, 3), 0)])
    assert d.copy() == d

    # find
    assert d.find(-1) == I.empty()
    assert d.find(0) == I.closed(0, 3)

    # init & update & eq
    d = I.IntervalDict({I.closed(0, 2): 0, I.closed(4, 5): 1})
    assert d == I.IntervalDict([(I.closed(0, 2), 0), (I.closed(4, 5), 1)])

    a, b = d.copy(), d.copy()
    a.update({I.closed(-1, 1): 2})
    b.update([[I.closed(-1, 1), 2]])
    assert a != d
    assert a == b
    assert a != 1
    assert a.items() == [(I.closed(-1, 1), 2), (I.openclosed(1, 2), 0), (I.closed(4, 5), 1)]

    assert I.IntervalDict([(0, 0), (1, 1)]) == I.IntervalDict([(1, 1), (0, 0)])


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
