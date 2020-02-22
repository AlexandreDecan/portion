import pytest

import intervals as I


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
