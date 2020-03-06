import pytest

import portion as P


class TestIterate:
    def test_default_parameters(self):
        assert list(P.iterate(P.closed(0, 2), step=1)) == [0, 1, 2]
        assert list(P.iterate(P.closedopen(0, 2), step=1)) == [0, 1]
        assert list(P.iterate(P.openclosed(0, 2), step=1)) == [1, 2]
        assert list(P.iterate(P.open(0, 2), step=1)) == [1]
        assert list(P.iterate(P.open(0, 2.5), step=1)) == [1, 2]

    def test_empty_intervals(self):
        assert list(P.iterate(P.empty(), step=1)) == []
        assert list(P.iterate(P.open(0, 1), step=1)) == []

    def test_open_intervals(self):
        with pytest.raises(ValueError):
            list(P.iterate(P.openclosed(-P.inf, 2), step=1))

        gen = P.iterate(P.closedopen(0, P.inf), step=1)
        assert next(gen) == 0
        assert next(gen) == 1
        assert next(gen) == 2  # and so on

    def test_with_gaps(self):
        assert list(P.iterate(P.closed(0, 1) | P.closed(5, 6), step=1)) == [0, 1, 5, 6]
        assert list(P.iterate(P.closed(0, 1) | P.closed(2.5, 4), step=1)) == [0, 1, 2.5, 3.5]
        assert list(P.iterate(P.open(0, 1) | P.open(1, 2), step=1)) == []
        assert list(P.iterate(P.open(0.5, 1) | P.open(1, 3), step=1)) == [2]

    def test_with_step(self):
        assert list(P.iterate(P.closed(0, 6), step=2)) == [0, 2, 4, 6]
        assert list(P.iterate(P.closed(0, 6), step=4)) == [0, 4]
        assert list(P.iterate(P.closed(0, 6), step=lambda x: x + 2)) == [0, 2, 4, 6]

    def test_with_base(self):
        assert list(P.iterate(P.closed(0.4, 2), step=1, base=lambda x: round(x))) == [1, 2]
        assert list(P.iterate(P.closed(0.6, 2), step=1, base=lambda x: round(x))) == [1, 2]

    def test_reversed_iteration(self):
        assert list(P.iterate(P.closed(0, 1), step=-1, reverse=True)) == [1, 0]
        assert list(P.iterate(P.open(0, 3), step=-1, reverse=True)) == [2, 1]
        assert list(P.iterate(P.closed(0, 1), step=-0.5, reverse=True)) == [1, 0.5, 0]
        assert list(P.iterate(P.closed(0, 2), step=-1, base=lambda x: x-1, reverse=True)) == [1, 0]
        assert list(P.iterate(P.closed(0, 2) | P.closed(4, 5), step=-1, reverse=True)) == [5, 4, 2, 1, 0]

    def test_reversed_iteration_with_open_intervals(self):
        with pytest.raises(ValueError):
            list(P.iterate(P.closedopen(0, P.inf), step=-1, reverse=True))

        gen = P.iterate(P.openclosed(-P.inf, 0), step=-1, reverse=True)
        assert next(gen) == 0
        assert next(gen) == -1
        assert next(gen) == -2  # and so on
