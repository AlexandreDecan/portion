import pytest

import intervals as I


class TestToString:
    def test_bounds(self):
        assert I.to_string(I.closed(0, 1)) == '[0,1]'
        assert I.to_string(I.openclosed(0, 1)) == '(0,1]'
        assert I.to_string(I.closedopen(0, 1)) == '[0,1)'
        assert I.to_string(I.open(0, 1)) == '(0,1)'

    def test_singleton(self):
        assert I.to_string(I.singleton(0)) == '[0]'

    def test_empty(self):
        assert I.to_string(I.empty()) == '()'

    def test_infinities(self):
        assert I.to_string(I.openclosed(-I.inf, 1)) == '(-inf,1]'
        assert I.to_string(I.closedopen(1, I.inf)) == '[1,+inf)'

    def test_unions(self):
        assert I.to_string(I.closed(0, 1) | I.closed(2, 3)) == '[0,1] | [2,3]'

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
    def test_bounds(self):
        assert I.from_string('[0,1]', int) == I.closed(0, 1)
        assert I.from_string('(0,1]', int) == I.openclosed(0, 1)
        assert I.from_string('[0,1)', int) == I.closedopen(0, 1)
        assert I.from_string('(0,1)', int) == I.open(0, 1)

    def test_singleton(self):
        assert I.from_string('[0]', int) == I.singleton(0)

    def test_empty(self):
        assert I.from_string('()', int) == I.empty()

    def test_infinities(self):
        assert I.from_string('(-inf,1]', int) == I.openclosed(-I.inf, 1)
        assert I.from_string('[1,+inf)', int) == I.closedopen(1, I.inf)

    def test_unions(self):
        assert I.from_string('[0,1] | [2,3]', int) == I.closed(0, 1) | I.closed(2, 3)

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
    def test_identity(self):
        i1, i2, i3, i4 = I.closed(0, 1), I.openclosed(0, 1), I.closedopen(0, 1), I.open(0, 1)

        assert I.from_string(I.to_string(i1), int) == i1
        assert I.from_string(I.to_string(i2), int) == i2
        assert I.from_string(I.to_string(i3), int) == i3
        assert I.from_string(I.to_string(i4), int) == i4


class TestToData:
    def test_bounds(self):
        assert I.to_data(I.closed(0, 1)) == [(I.CLOSED, 0, 1, I.CLOSED)]
        assert I.to_data(I.openclosed(0, 1)) == [(I.OPEN, 0, 1, I.CLOSED)]
        assert I.to_data(I.closedopen(0, 1)) == [(I.CLOSED, 0, 1, I.OPEN)]
        assert I.to_data(I.open(0, 1)) == [(I.OPEN, 0, 1, I.OPEN)]

    def test_values(self):
        assert I.to_data(I.closed('a', 'b')) == [(I.CLOSED, 'a', 'b', I.CLOSED)]
        assert I.to_data(I.closed(tuple([0]), tuple([1]))) == [(I.CLOSED, (0,), (1,), I.CLOSED)]

    def test_singleton(self):
        assert I.to_data(I.singleton(0)) == [(I.CLOSED, 0, 0, I.CLOSED)]

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
    def test_bounds(self):
        assert I.from_data([(I.CLOSED, 0, 1, I.CLOSED)]) == I.closed(0, 1)
        assert I.from_data([(I.OPEN, 0, 1, I.CLOSED)]) == I.openclosed(0, 1)
        assert I.from_data([(I.CLOSED, 0, 1, I.OPEN)]) == I.closedopen(0, 1)
        assert I.from_data([(I.OPEN, 0, 1, I.OPEN)]) == I.open(0, 1)

    def test_values(self):
        assert I.from_data([(I.CLOSED, 'a', 'b', I.CLOSED)]) == I.closed('a', 'b')
        assert I.from_data([(I.CLOSED, (0,), (1,), I.CLOSED)]) == I.closed(tuple([0]), tuple([1]))

    def test_singleton(self):
        assert I.from_data([(I.CLOSED, 0, 0, I.CLOSED)]) == I.singleton(0)

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
    def test_identity(self):
        i1, i2, i3, i4 = I.closed(0, 1), I.openclosed(0, 1), I.closedopen(0, 1), I.open(0, 1)

        assert I.from_data(I.to_data(i2)) == i2
        assert I.from_data(I.to_data(i3)) == i3
        assert I.from_data(I.to_data(i4)) == i4
        assert I.from_data(I.to_data(i1)) == i1