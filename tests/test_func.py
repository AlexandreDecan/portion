import pytest
import intervals as I
import hypothesis.strategies as st

from hypothesis import given, example, assume
from .strategies import values


class TestIterate:
    def test_default_parameters(self):
        assert list(I.iterate(I.closed(0, 2), incr=1)) == [0, 1, 2]
        assert list(I.iterate(I.closedopen(0, 2), incr=1)) == [0, 1]
        assert list(I.iterate(I.openclosed(0, 2), incr=1)) == [1, 2]
        assert list(I.iterate(I.open(0, 2), incr=1)) == [1]
        assert list(I.iterate(I.open(0, 2.5), incr=1)) == [1, 2]

    @example(0, 0, 1, False)
    @example(0, 0, 1, True)
    @given(values, values, st.integers(1), st.booleans())
    def test_contain_values(self, lower, upper, incr, reverse):
        assume(lower <= upper)

        if not reverse:
            r = range(lower, upper + incr, incr)
        else:
            r = range(upper, lower - incr, -incr)

        assert list(I.iterate(I.closed(lower, upper), incr=incr, reverse=reverse)) == list(filter(lambda x: lower <= x <= upper, r))
        assert list(I.iterate(I.openclosed(lower, upper), incr=incr, reverse=reverse)) == list(filter(lambda x: lower < x <= upper, r))
        assert list(I.iterate(I.closedopen(lower, upper), incr=incr, reverse=reverse)) == list(filter(lambda x: lower <= x < upper, r))
        assert list(I.iterate(I.open(lower, upper), incr=incr, reverse=reverse)) == list(filter(lambda x: lower < x < upper, r))

    def test_empty_intervals(self):
        assert list(I.iterate(I.empty(), incr=1)) == []

    @given(values, st.integers(1))
    def test_infinities(self, value, incr):
        with pytest.raises(ValueError):
            list(I.iterate(I.openclosed(-I.inf, value), incr=incr))

        gen = I.iterate(I.closedopen(value, I.inf), incr=incr)
        assert next(gen) == value
        assert next(gen) == value + incr
        assert next(gen) == value + 2 * incr  # and so on

    def test_with_gaps(self):
        assert list(I.iterate(I.closed(0, 1) | I.closed(5, 6), incr=1)) == [0, 1, 5, 6]
        assert list(I.iterate(I.closed(0, 1) | I.closed(2.5, 4), incr=1)) == [0, 1, 2.5, 3.5]
        assert list(I.iterate(I.open(0, 1) | I.open(1, 2), incr=1)) == []
        assert list(I.iterate(I.open(0.5, 1) | I.open(1, 3), incr=1)) == [2]

    def test_with_step_function(self):
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

    @given(values, st.integers(1))
    def test_reversed_iteration_with_open_intervals(self, value, incr):
        with pytest.raises(ValueError):
            list(I.iterate(I.closedopen(value, I.inf), incr=incr, reverse=True))

        gen = I.iterate(I.openclosed(-I.inf, value), incr=incr, reverse=True)
        assert next(gen) == value
        assert next(gen) == value - incr
        assert next(gen) == value - 2 * incr  # and so on
