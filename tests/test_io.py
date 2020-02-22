import pytest
import intervals as I
import hypothesis.strategies as st

from hypothesis import given, assume, example
from .strategies import intervals, values


class TestToString:
    @given(values, values)
    def test_bounds(self, x, y):
        assume(x < y)
        assert I.to_string(I.closed(x, y)) == '[{},{}]'.format(x, y)
        assert I.to_string(I.openclosed(x, y)) == '({},{}]'.format(x, y)
        assert I.to_string(I.closedopen(x, y)) == '[{},{})'.format(x, y)
        assert I.to_string(I.open(x, y)) == '({},{})'.format(x, y)

    @given(values)
    def test_singleton(self, x):
        assert I.to_string(I.singleton(x)) == '[{}]'.format(x)

    def test_empty(self):
        assert I.to_string(I.empty()) == '()'

    @given(values)
    def test_infinities(self, x):
        assert I.to_string(I.openclosed(-I.inf, x)) == '(-inf,{}]'.format(x)
        assert I.to_string(I.closedopen(x, I.inf)) == '[{},+inf)'.format(x)

    @given(st.tuples(values, values, values, values))
    def test_unions(self, t):
        a, b, x, y = sorted(t)
        assume(a < b < x < y)
        assert I.to_string(I.closed(a, b) | I.closed(x, y)) == '[{},{}] | [{},{}]'.format(a, b, x, y)

    def test_bound_types(self):
        assert I.to_string(I.closed('a', 'b')) == "['a','b']"
        assert I.to_string(I.closed(tuple([0]), tuple([1]))) == '[(0,),(1,)]'

    def test_parameters(self):
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


class TestFromString:
    @given(values, values)
    def test_bounds(self, x, y):
        assume(x < y)
        assert I.from_string('[{},{}]'.format(x, y), int) == I.closed(x, y)
        assert I.from_string('({},{}]'.format(x, y), int) == I.openclosed(x, y)
        assert I.from_string('[{},{})'.format(x, y), int) == I.closedopen(x, y)
        assert I.from_string('({},{})'.format(x, y), int) == I.open(x, y)

    @given(values)
    def test_singleton(self, x):
        assert I.from_string('[{}]'.format(x), int) == I.singleton(x)
        assert I.from_string('[{},{}]'.format(x, x), int) == I.singleton(x)

    def test_empty(self):
        assert I.from_string('()', int) == I.empty()

    @given(values)
    def test_infinities(self, x):
        assert I.from_string('(-inf,{}]'.format(x), int) == I.openclosed(-I.inf, x)
        assert I.from_string('[{},+inf)'.format(x), int) == I.closedopen(x, I.inf)

    @given(st.tuples(values, values, values, values))
    def test_unions(self, t):
        a, b, x, y = sorted(t)
        assume(a < b < x < y)
        assert I.from_string('[{},{}] | [{},{}]'.format(a, b, x, y), int) == I.closed(a, b) | I.closed(x, y)

    def test_conv_is_required(self):
        with pytest.raises(Exception):
            I.from_string('[1,2]', None)

    def test_parameters(self):
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


class TestStringIdentity:
    @example(I.closed(0, 1))
    @example(I.openclosed(0, 1))
    @example(I.closedopen(0, 1))
    @example(I.open(0, 1))
    @example(I.singleton(0))
    @example(I.empty())
    @given(intervals())
    def test_identity(self, x):
        assert I.from_string(I.to_string(x), int) == x


class TestToData:
    @given(values, values)
    def test_bounds(self, x, y):
        assume(x < y)
        assert I.to_data(I.closed(x, y)) == [(I.CLOSED, x, y, I.CLOSED)]
        assert I.to_data(I.openclosed(x, y)) == [(I.OPEN, x, y, I.CLOSED)]
        assert I.to_data(I.closedopen(x, y)) == [(I.CLOSED, x, y, I.OPEN)]
        assert I.to_data(I.open(x, y)) == [(I.OPEN, x, y, I.OPEN)]

    def test_values(self):
        assert I.to_data(I.closed('a', 'b')) == [(I.CLOSED, 'a', 'b', I.CLOSED)]
        assert I.to_data(I.closed(tuple([0]), tuple([1]))) == [(I.CLOSED, (0,), (1,), I.CLOSED)]

    @given(values)
    def test_singleton(self, x):
        assert I.to_data(I.singleton(x)) == [(I.CLOSED, x, x, I.CLOSED)]

    def test_open_intervals(self):
        assert I.to_data(I.open(-I.inf, I.inf)) == [(I.OPEN, float('-inf'), float('inf'), I.OPEN)]
        assert I.to_data(I.openclosed(-I.inf, 0)) == [(I.OPEN, float('-inf'), 0, I.CLOSED)]
        assert I.to_data(I.closedopen(0, I.inf)) == [(I.CLOSED, 0, float('inf'), I.OPEN)]

    def test_empty_interval(self):
        assert I.to_data(I.empty()) == [(I.OPEN, float('inf'), float('-inf'), I.OPEN)]

    def test_unions(self):
        i = I.openclosed(-I.inf, 4) | I.closedopen(6, I.inf)
        assert I.to_data(i) == [(I.OPEN, float('-inf'), 4, I.CLOSED), (I.CLOSED, 6, float('inf'), I.OPEN)]

    def test_parameters(self):
        i = I.openclosed(-I.inf, 4) | I.closedopen(6, I.inf)
        assert I.to_data(i, conv=str, pinf='highest', ninf='lowest') == [(I.OPEN, 'lowest', '4', I.CLOSED), (I.CLOSED, '6', 'highest', I.OPEN)]


class TestFromData:
    @given(values, values)
    def test_bounds(self, x, y):
        assume(x < y)
        assert I.from_data([(I.CLOSED, x, y, I.CLOSED)]) == I.closed(x, y)
        assert I.from_data([(I.OPEN, x, y, I.CLOSED)]) == I.openclosed(x, y)
        assert I.from_data([(I.CLOSED, x, y, I.OPEN)]) == I.closedopen(x, y)
        assert I.from_data([(I.OPEN, x, y, I.OPEN)]) == I.open(x, y)

    def test_values(self):
        assert I.from_data([(I.CLOSED, 'a', 'b', I.CLOSED)]) == I.closed('a', 'b')
        assert I.from_data([(I.CLOSED, (0,), (1,), I.CLOSED)]) == I.closed(tuple([0]), tuple([1]))

    @given(values)
    def test_singleton(self, x):
        assert I.from_data([(I.CLOSED, x, x, I.CLOSED)]) == I.singleton(x)

    def test_open_intervals(self):
        assert I.from_data([(I.OPEN, float('-inf'), float('inf'), I.OPEN)]) == I.open(-I.inf, I.inf)
        assert I.from_data([(I.OPEN, float('-inf'), 0, I.CLOSED)]) == I.openclosed(-I.inf, 0)
        assert I.from_data([(I.CLOSED, 0, float('inf'), I.OPEN)]) == I.closedopen(0, I.inf)

    def test_empty_interval(self):
        assert I.from_data([(I.OPEN, float('inf'), float('-inf'), I.OPEN)]) == I.empty()

    def test_unions(self):
        d = [(I.OPEN, float('-inf'), 4, I.CLOSED), (I.CLOSED, 6, float('inf'), I.OPEN)]
        assert I.from_data(d) == I.openclosed(-I.inf, 4) | I.closedopen(6, I.inf)

    def test_parameters(self):
        d = [(I.OPEN, 'lowest', '4', I.CLOSED), (I.CLOSED, '6', 'highest', I.OPEN)]
        assert I.from_data(d, conv=int, pinf='highest', ninf='lowest') == I.openclosed(-I.inf, 4) | I.closedopen(6, I.inf)


class TestDataIdentity:
    @example(I.closed(0, 1))
    @example(I.openclosed(0, 1))
    @example(I.closedopen(0, 1))
    @example(I.open(0, 1))
    @example(I.singleton(0))
    @example(I.empty())
    @given(intervals())
    def test_identity(self, i):
        assert I.from_data(I.to_data(i)) == i