import pytest

import intervals as I


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

