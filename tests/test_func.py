import pytest

import intervals as I


class TestIterate:
    def test_default_parameters(self):
        assert list(I.iterate(I.closed(0, 2), incr=1)) == [0, 1, 2]
        assert list(I.iterate(I.closedopen(0, 2), incr=1)) == [0, 1]
        assert list(I.iterate(I.openclosed(0, 2), incr=1)) == [1, 2]
        assert list(I.iterate(I.open(0, 2), incr=1)) == [1]
        assert list(I.iterate(I.open(0, 2.5), incr=1)) == [1, 2]

    def test_empty_intervals(self):
        assert list(I.iterate(I.empty(), incr=1)) == []
        assert list(I.iterate(I.open(0, 1), incr=1)) == []

    def test_open_intervals(self):
        with pytest.raises(ValueError):
            list(I.iterate(I.openclosed(-I.inf, 2), incr=1))

        gen = I.iterate(I.closedopen(0, I.inf), incr=1)
        assert next(gen) == 0
        assert next(gen) == 1
        assert next(gen) == 2  # and so on

    def test_with_gaps(self):
        assert list(I.iterate(I.closed(0, 1) | I.closed(5, 6), incr=1)) == [0, 1, 5, 6]
        assert list(I.iterate(I.closed(0, 1) | I.closed(2.5, 4), incr=1)) == [0, 1, 2.5, 3.5]
        assert list(I.iterate(I.open(0, 1) | I.open(1, 2), incr=1)) == []
        assert list(I.iterate(I.open(0.5, 1) | I.open(1, 3), incr=1)) == [2]

    def test_with_step(self):
        assert list(I.iterate(I.closed(0, 6), incr=2)) == [0, 2, 4, 6]
        assert list(I.iterate(I.closed(0, 6), incr=4)) == [0, 4]
        assert list(I.iterate(I.closed(0, 6), incr=lambda x: x + 2)) == [0, 2, 4, 6]

    def test_with_base(self):
        assert list(I.iterate(I.closed(0.4, 2), incr=1, base=lambda x: round(x))) == [1, 2]
        assert list(I.iterate(I.closed(0.6, 2), incr=1, base=lambda x: round(x))) == [1, 2]

    def test_reversed_iteration(self):
        assert list(I.iterate(I.closed(0, 1), incr=1, reverse=True)) == [1, 0]
        assert list(I.iterate(I.open(0, 3), incr=1, reverse=True)) == [2, 1]
        assert list(I.iterate(I.closed(0, 1), incr=0.5, reverse=True)) == [1, 0.5, 0]
        assert list(I.iterate(I.closed(0, 2), incr=1, base=lambda x: x-1, reverse=True)) == [1, 0]
        assert list(I.iterate(I.closed(0, 2) | I.closed(4, 5), incr=1, reverse=True)) == [5, 4, 2, 1, 0]

    def test_reversed_iteration_with_open_intervals(self):
        with pytest.raises(ValueError):
            list(I.iterate(I.closedopen(0, I.inf), incr=1, reverse=True))

        gen = I.iterate(I.openclosed(-I.inf, 0), incr=1, reverse=True)
        assert next(gen) == 0
        assert next(gen) == -1
        assert next(gen) == -2  # and so on