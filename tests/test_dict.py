import pytest

import portion as P


class TestIntervalDict:
    def test_with_single_values(self):
        d = P.IntervalDict()

        # Single value
        d[P.closed(0, 2)] = 0
        assert len(d) == 1
        assert d[2] == 0
        assert d.get(2) == 0
        with pytest.raises(KeyError):
            d[3]
        assert d.get(3) is None

    def test_with_intervals(self):
        d = P.IntervalDict([(P.closed(0, 2), 0)])
        assert d[P.open(-P.inf, P.inf)].as_dict() == {P.closed(0, 2): 0}
        assert d[P.closed(0, 2)].as_dict() == {P.closed(0, 2): 0}
        assert d[P.closed(-1, 0)].as_dict() == {P.singleton(0): 0}
        assert d[P.closed(-2, -1)].as_dict() == {}
        assert d.get(P.closed(0, 2)).as_dict() == {P.closed(0, 2): 0}
        assert d.get(P.closed(-2, -1)).as_dict() == {P.closed(-2, -1): None}
        assert d.get(P.closed(-1, 0)).as_dict() == {P.closedopen(-1, 0): None, P.singleton(0): 0}

        d[P.closed(1, 3)] = 1
        assert d.as_dict() == {P.closedopen(0, 1): 0, P.closed(1, 3): 1}
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

    def test_set(self):
        # Set values
        d = P.IntervalDict([(P.closed(0, 2), 0)])
        d[3] = 2
        assert d.as_dict() == {P.closed(0, 2): 0, P.singleton(3): 2}
        d[3] = 3
        assert d.as_dict() == {P.closed(0, 2): 0, P.singleton(3): 3}
        d[P.closed(0, 2)] = 1
        assert d.as_dict() == {P.closed(0, 2): 1, P.singleton(3): 3}
        d[P.closed(-1, 1)] = 2
        assert d.as_dict() == {P.closed(-1, 1): 2, P.openclosed(1, 2): 1, P.singleton(3): 3}

        d = P.IntervalDict([(P.closed(0, 2), 0)])
        d[P.closed(-1, 4)] = 1
        assert d.as_dict() == {P.closed(-1, 4): 1}
        d[P.closed(5, 6)] = 1
        assert d.as_dict() == {P.closed(-1, 4) | P.closed(5, 6): 1}

    def test_delete_value(self):
        d = P.IntervalDict([(P.closed(0, 2), 0)])
        del d[1]
        assert d.get(1, None) is None

    def test_delete_missing_value(self):
        d = P.IntervalDict([(P.closed(0, 2), 0)])
        with pytest.raises(KeyError):
            del d[3]

        del d[1]
        with pytest.raises(KeyError):
            d[1]

    def test_delete_interval(self):
        d = P.IntervalDict([(P.closed(0, 2), 0)])
        del d[P.closed(-1, 1)]
        assert d.as_dict() == {P.openclosed(1, 2): 0}

    def test_delete_interval_out_of_bound(self):
        d = P.IntervalDict([(P.closed(0, 2), 0)])
        del d[P.closed(-10, -9)]
        assert d.as_dict() == {P.closed(0, 2): 0}

    def test_delete_empty_interval(self):
        d = P.IntervalDict([(P.closed(0, 2), 0)])
        del d[P.empty()]
        assert d.as_dict() == {P.closed(0, 2): 0}

    def test_setdefault_with_values(self):
        d = P.IntervalDict([(P.closed(0, 2), 0)])
        assert d.setdefault(-1, default=0) == 0
        assert d[-1] == 0
        assert d.setdefault(0, default=1) == 0
        assert d[0] == 0

    def test_setdefault_with_intervals(self):
        d = P.IntervalDict([(P.closed(0, 2), 0)])
        t = d.setdefault(P.closed(-2, -1), -1)
        assert t.as_dict() == {P.closed(-2, -1): -1}
        assert d.as_dict() == {P.closed(-2, -1): -1, P.closed(0, 2): 0}

        d = P.IntervalDict([(P.closed(0, 2), 0)])
        t = d.setdefault(P.closed(-1, 1), 2)
        assert t.as_dict() == {P.closedopen(-1, 0): 2, P.closed(0, 1): 0}
        assert d.as_dict() == {P.closedopen(-1, 0): 2, P.closed(0, 2): 0}

    def test_iterators(self):
        d = P.IntervalDict([(P.closedopen(0, 1), 0), (P.closedopen(1, 3), 1), (P.singleton(3), 2)])

        assert set(d.keys()) == {P.closedopen(0, 1), P.closedopen(1, 3), P.singleton(3)}
        assert d.domain() == P.closed(0, 3)
        assert set(d.values()) == {0, 1, 2}
        assert set(d.items()) == {
            (P.closedopen(0, 1), 0),
            (P.closedopen(1, 3), 1),
            (P.singleton(3), 2),
        }
        assert set(d) == set(d.keys())

    def test_iterators_on_empty(self):
        assert len(P.IntervalDict().values()) == 0
        assert len(P.IntervalDict().as_dict()) == 0
        assert len(P.IntervalDict().keys()) == 0
        assert P.IntervalDict().domain() == P.empty()

    def test_views(self):
        d = P.IntervalDict({P.closed(0, 2): 3, P.closed(3, 4): 2})

        k, v, i = d.keys(), d.values(), d.items()
        assert len(k) == len(v) == len(i) == len(d)
        assert list(k) == [P.closed(0, 2), P.closed(3, 4)]
        assert list(v) == [3, 2]
        assert list(i) == [(P.closed(0, 2), 3), (P.closed(3, 4), 2)]

        d[5] = 4
        assert list(k) == list(d.keys())
        assert list(v) == list(d.values())
        assert list(i) == list(d.items())

    def test_issue_39(self):
        # https://github.com/AlexandreDecan/portion/issues/39
        d = P.IntervalDict({P.open(2, 3): 1, P.singleton(2): 2})
        assert list(d) == list([P.singleton(2), P.open(2, 3)])

    def test_combine_empty(self):
        def add(x, y): return x + y
        assert P.IntervalDict().combine(P.IntervalDict(), add) == P.IntervalDict()

        d = P.IntervalDict([(P.closed(0, 3), 0)])
        assert P.IntervalDict().combine(d, add) == d
        assert d.combine(P.IntervalDict(), add) == d

    def test_combine_nonempty(self):
        def add(x, y): return x + y
        d1 = P.IntervalDict([(P.closed(1, 3) | P.closed(5, 7), 1)])
        d2 = P.IntervalDict([(P.closed(2, 4) | P.closed(6, 8), 2)])
        assert d1.combine(d2, add) == d2.combine(d1, add)
        assert d1.combine(d2, add) == P.IntervalDict([
            (P.closedopen(1, 2) | P.closedopen(5, 6), 1),
            (P.closed(2, 3) | P.closed(6, 7), 3),
            (P.openclosed(3, 4) | P.openclosed(7, 8), 2),
        ])

        d1 = P.IntervalDict({
            P.closed(0, 1): 2,
            P.closed(3, 4): 2
        })
        d2 = P.IntervalDict({
            P.closed(1, 3): 3,
            P.closed(4, 5): 1
        })
        assert d1.combine(d2, add) == d2.combine(d1, add)
        assert d1.combine(d2, add) == P.IntervalDict({
            P.closedopen(0, 1): 2,
            P.singleton(1): 5,
            P.open(1, 3): 3,
            P.singleton(3): 5,
            P.open(3, 4): 2,
            P.singleton(4): 3,
            P.openclosed(4, 5): 1,
        })

    def test_containment(self):
        d = P.IntervalDict([(P.closed(0, 3), 0)])
        assert 0 in d
        assert -1 not in d
        assert P.closed(-2, -1) not in d
        assert P.closed(1, 2) in d
        assert P.closed(1, 4) not in d

    def test_or_ior(self):
        # https://github.com/AlexandreDecan/portion/issues/37
        d1 = P.IntervalDict({P.closed(0, 1): 1, P.closed(3, 4): 2})
        d2 = P.IntervalDict({P.closed(0.5, 2): 3})

        assert d1 | d2 == P.IntervalDict({
            P.closedopen(0, 0.5): 1,
            P.closed(0.5, 2): 3,
            P.closed(3, 4): 2
        })
        assert d1 == P.IntervalDict({P.closed(0, 1): 1, P.closed(3, 4): 2})
        assert d2 == P.IntervalDict({P.closed(0.5, 2): 3})

        d1 |= d2
        assert d1 == P.IntervalDict({
            P.closedopen(0, 0.5): 1,
            P.closed(0.5, 2): 3,
            P.closed(3, 4): 2
        })
        assert d2 == P.IntervalDict({P.closed(0.5, 2): 3})

    def test_repr(self):
        d = P.IntervalDict([(P.closed(0, 3), 0)])
        assert repr(d) == '{' + repr(P.closed(0, 3)) + ': 0}'

    def test_pop_value(self):
        d = P.IntervalDict([(P.closed(0, 3), 0)])
        t = d.pop(2)
        assert t == 0
        assert d.get(2, None) is None

    def test_pop_missing_value(self):
        d = P.IntervalDict([(P.closed(0, 3), 0)])
        with pytest.raises(KeyError):
            d.pop(4)

        t = d.pop(4, 1)
        assert t == 1

    def test_pop_interval(self):
        d = P.IntervalDict([(P.closed(0, 3), 0)])
        t = d.pop(P.closed(0, 1))
        assert t.as_dict() == {P.closed(0, 1): 0}
        assert d.as_dict() == {P.openclosed(1, 3): 0}

        t = d.pop(P.closed(0, 2), 1)
        assert t.as_dict() == {P.closed(0, 1): 1, P.openclosed(1, 2): 0}
        assert d.as_dict() == {P.openclosed(2, 3): 0}

    def test_popitem(self):
        d = P.IntervalDict([(P.closed(0, 3), 0)])
        t = d.popitem()
        assert t == (P.closed(0, 3), 0)
        assert len(d) == 0

    def test_popitem_with_empty(self):
        with pytest.raises(KeyError):
            P.IntervalDict().popitem()

    def test_clear(self):
        d = P.IntervalDict([(P.closed(0, 3), 0)])
        d.clear()
        assert d == P.IntervalDict()
        d.clear()
        assert d == P.IntervalDict()

    def test_find(self):
        d = P.IntervalDict([(P.closed(0, 3), 0)])
        assert d.find(-1) == P.empty()
        assert d.find(0) == P.closed(0, 3)

    def test_find_on_unions(self):
        d = P.IntervalDict([(P.closed(0, 2), 0), (P.closed(3, 5), 0), (P.closed(7, 9), 1)])
        assert d.find(1) == P.closed(7, 9)
        assert d.find(0) == P.closed(0, 2) | P.closed(3, 5)

    def test_copy(self):
        d = P.IntervalDict([(P.closed(0, 3), 0)])
        assert d.copy() == d
        assert d.copy() is not d

    def test_copy_and_update(self):
        d = P.IntervalDict({P.closed(0, 2): 0, P.closed(4, 5): 1})
        assert d == P.IntervalDict([(P.closed(0, 2), 0), (P.closed(4, 5), 1)])

        a, b = d.copy(), d.copy()
        a.update({P.closed(-1, 1): 2})
        b.update([[P.closed(-1, 1), 2]])
        assert a != d
        assert a == b
        assert a != 1
        assert a.as_dict() == {P.closed(-1, 1): 2, P.openclosed(1, 2): 0, P.closed(4, 5): 1}

        assert P.IntervalDict([(0, 0), (1, 1)]) == P.IntervalDict([(1, 1), (0, 0)])

    def test_update_with_intervaldict(self):
        d = P.IntervalDict()
        d2 = P.IntervalDict()

        d[1] = 'c'
        d2[1] = 'a'
        d2[2] = 'b'

        d.update(d2)
        assert d[1] == 'a'
        assert d[2] == 'b'
        assert len(d) == 2

    def test_update_with_mapping(self):
        d = P.IntervalDict()
        d2 = {1: 'a', 2: 'b'}

        d.update(d2)
        assert d[1] == 'a'
        assert d[2] == 'b'
        assert len(d) == 2

    def test_update_with_iterable(self):
        d = P.IntervalDict()
        d2 = {1: 'a', 2: 'b'}

        d.update(d2.items())
        assert d[1] == 'a'
        assert d[2] == 'b'
        assert len(d) == 2
