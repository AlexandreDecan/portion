import pytest

import portion as P


class TestToString:
    def test_bounds(self):
        assert P.to_string(P.closed(0, 1)) == '[0,1]'
        assert P.to_string(P.openclosed(0, 1)) == '(0,1]'
        assert P.to_string(P.closedopen(0, 1)) == '[0,1)'
        assert P.to_string(P.open(0, 1)) == '(0,1)'

    def test_singleton(self):
        assert P.to_string(P.singleton(0)) == '[0]'

    def test_empty(self):
        assert P.to_string(P.empty()) == '()'

    def test_infinities(self):
        assert P.to_string(P.openclosed(-P.inf, 1)) == '(-inf,1]'
        assert P.to_string(P.closedopen(1, P.inf)) == '[1,+inf)'

    def test_unions(self):
        assert P.to_string(P.closed(0, 1) | P.closed(2, 3)) == '[0,1] | [2,3]'

    def test_bound_types(self):
        assert P.to_string(P.closed('a', 'b')) == "['a','b']"
        assert P.to_string(P.closed(tuple([0]), tuple([1]))) == '[(0,),(1,)]'

    def test_parameters(self):
        i1, i2, i3, i4 = P.closed(0, 1), P.openclosed(0, 1), P.closedopen(0, 1), P.open(0, 1)
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

        assert P.to_string(i1, **params) == '<"0"-"1">'
        assert P.to_string(i2, **params) == '<!"0"-"1">'
        assert P.to_string(i3, **params) == '<"0"-"1"!>'
        assert P.to_string(i4, **params) == '<!"0"-"1"!>'

        assert P.to_string(P.empty(), **params) == '<!!>'
        assert P.to_string(P.singleton(1), **params) == '<"1">'

        assert P.to_string(P.openclosed(-P.inf, 1), **params) == '<!-oo-"1">'
        assert P.to_string(P.closedopen(1, P.inf), **params) == '<"1"-+oo!>'

        assert P.to_string(P.closed(0, 1) | P.closed(2, 3), **params) == '<"0"-"1"> or <"2"-"3">'


class TestFromString:
    def test_bounds(self):
        assert P.from_string('[0,1]', int) == P.closed(0, 1)
        assert P.from_string('(0,1]', int) == P.openclosed(0, 1)
        assert P.from_string('[0,1)', int) == P.closedopen(0, 1)
        assert P.from_string('(0,1)', int) == P.open(0, 1)

    def test_singleton(self):
        assert P.from_string('[0]', int) == P.singleton(0)

    def test_empty(self):
        assert P.from_string('()', int) == P.empty()

    def test_infinities(self):
        assert P.from_string('(-inf,1]', int) == P.openclosed(-P.inf, 1)
        assert P.from_string('[1,+inf)', int) == P.closedopen(1, P.inf)

    def test_unions(self):
        assert P.from_string('[0,1] | [2,3]', int) == P.closed(0, 1) | P.closed(2, 3)

    def test_conv_is_required(self):
        with pytest.raises(Exception):
            P.from_string('[1,2]', None)

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

        assert P.from_string(i1, **params) == P.closed(0, 1)
        assert P.from_string(i2, **params) == P.openclosed(0, 1)
        assert P.from_string(i3, **params) == P.closedopen(0, 1)
        assert P.from_string(i4, **params) == P.open(0, 1)

        assert P.from_string('<!!>', **params) == P.empty()
        assert P.from_string('<"1">', **params) == P.singleton(1)

        assert P.from_string('<!-oo-"1">', **params) == P.openclosed(-P.inf, 1)
        assert P.from_string('<"1"-+oo!>', **params) == P.closedopen(1, P.inf)

        assert P.from_string('<"0"-"1"> or <"2"-"3">', **params) == P.closed(0, 1) | P.closed(2, 3)

    @pytest.mark.parametrize('case', [
        ' ',
        '1',
        '[1',
        '1)',
        ')1,2]',
        '|',
        '[0,1] | ',
        '[0,1] | 1',
        '1 | [0,1]',
        '[0,1] | 1 | [2,3]',
        '[0,1] || [2,3]',
    ])
    def test_invalid_strings(self, case):
        # Related to https://github.com/AlexandreDecan/portion/issues/57
        with pytest.raises(ValueError):
            P.from_string(case, int)


class TestStringIdentity:
    def test_identity(self):
        i1, i2, i3, i4 = P.closed(0, 1), P.openclosed(0, 1), P.closedopen(0, 1), P.open(0, 1)

        assert P.from_string(P.to_string(i1), int) == i1
        assert P.from_string(P.to_string(i2), int) == i2
        assert P.from_string(P.to_string(i3), int) == i3
        assert P.from_string(P.to_string(i4), int) == i4


class TestToData:
    def test_bounds(self):
        assert P.to_data(P.closed(0, 1)) == [(True, 0, 1, True)]
        assert P.to_data(P.openclosed(0, 1)) == [(False, 0, 1, True)]
        assert P.to_data(P.closedopen(0, 1)) == [(True, 0, 1, False)]
        assert P.to_data(P.open(0, 1)) == [(False, 0, 1, False)]

    def test_values(self):
        assert P.to_data(P.closed('a', 'b')) == [(True, 'a', 'b', True)]
        assert P.to_data(P.closed(tuple([0]), tuple([1]))) == [(True, (0,), (1,), True)]

    def test_singleton(self):
        assert P.to_data(P.singleton(0)) == [(True, 0, 0, True)]

    def test_open_intervals(self):
        assert P.to_data(P.open(-P.inf, P.inf)) == [(False, float('-inf'), float('inf'), False)]
        assert P.to_data(P.openclosed(-P.inf, 0)) == [(False, float('-inf'), 0, True)]
        assert P.to_data(P.closedopen(0, P.inf)) == [(True, 0, float('inf'), False)]

    def test_empty_interval(self):
        assert P.to_data(P.empty()) == [(False, float('inf'), float('-inf'), False)]

    def test_unions(self):
        i = P.openclosed(-P.inf, 4) | P.closedopen(6, P.inf)
        assert P.to_data(i) == [(False, float('-inf'), 4, True), (True, 6, float('inf'), False)]

    def test_parameters(self):
        i = P.openclosed(-P.inf, 4) | P.closedopen(6, P.inf)
        assert P.to_data(i, conv=str, pinf='highest', ninf='lowest') == [(False, 'lowest', '4', True), (True, '6', 'highest', False)]


class TestFromData:
    def test_bounds(self):
        assert P.from_data([(P.CLOSED, 0, 1, P.CLOSED)]) == P.closed(0, 1)
        assert P.from_data([(P.OPEN, 0, 1, P.CLOSED)]) == P.openclosed(0, 1)
        assert P.from_data([(P.CLOSED, 0, 1, P.OPEN)]) == P.closedopen(0, 1)
        assert P.from_data([(P.OPEN, 0, 1, P.OPEN)]) == P.open(0, 1)

    def test_values(self):
        assert P.from_data([(P.CLOSED, 'a', 'b', P.CLOSED)]) == P.closed('a', 'b')
        assert P.from_data([(P.CLOSED, (0,), (1,), P.CLOSED)]) == P.closed(tuple([0]), tuple([1]))

    def test_singleton(self):
        assert P.from_data([(P.CLOSED, 0, 0, P.CLOSED)]) == P.singleton(0)

    def test_open_intervals(self):
        assert P.from_data([(P.OPEN, float('-inf'), float('inf'), P.OPEN)]) == P.open(-P.inf, P.inf)
        assert P.from_data([(P.OPEN, float('-inf'), 0, P.CLOSED)]) == P.openclosed(-P.inf, 0)
        assert P.from_data([(P.CLOSED, 0, float('inf'), P.OPEN)]) == P.closedopen(0, P.inf)

    def test_empty_interval(self):
        assert P.from_data([(P.OPEN, float('inf'), float('-inf'), P.OPEN)]) == P.empty()

    def test_unions(self):
        d = [(P.OPEN, float('-inf'), 4, P.CLOSED), (P.CLOSED, 6, float('inf'), P.OPEN)]
        assert P.from_data(d) == P.openclosed(-P.inf, 4) | P.closedopen(6, P.inf)

    def test_parameters(self):
        d = [(P.OPEN, 'lowest', '4', P.CLOSED), (P.CLOSED, '6', 'highest', P.OPEN)]
        assert P.from_data(d, conv=int, pinf='highest', ninf='lowest') == P.openclosed(-P.inf, 4) | P.closedopen(6, P.inf)


class TestDataIdentity:
    def test_identity(self):
        i1, i2, i3, i4 = P.closed(0, 1), P.openclosed(0, 1), P.closedopen(0, 1), P.open(0, 1)

        assert P.from_data(P.to_data(i2)) == i2
        assert P.from_data(P.to_data(i3)) == i3
        assert P.from_data(P.to_data(i4)) == i4
        assert P.from_data(P.to_data(i1)) == i1
