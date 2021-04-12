import pytest

from portion.const import inf, _PInf, _NInf, Bound
from portion import CLOSED, OPEN


class TestBounds:
    def test_comparisons(self):
        assert CLOSED == Bound.CLOSED
        assert OPEN == Bound.OPEN
        assert CLOSED != OPEN
        assert OPEN != CLOSED

    def test_non_Boolean(self):
        with pytest.raises(ValueError):
            assert not OPEN

        with pytest.raises(ValueError):
            assert not CLOSED

    def test_value(self):
        assert Bound(True) == Bound.CLOSED
        assert Bound(False) == Bound.OPEN

        assert Bound.CLOSED.value is True
        assert Bound.OPEN.value is False


class TestInfinities:
    def test_pinf_is_greater(self):
        assert not (inf > inf)
        assert inf > -inf
        assert inf > 0
        assert inf > 'a'
        assert inf > []

        assert inf >= inf
        assert inf >= -inf
        assert inf >= 0
        assert inf >= 'a'
        assert inf >= []

    def test_ninf_is_lower(self):
        assert not (-inf < -inf)
        assert -inf < inf
        assert -inf < 0
        assert -inf < 'a'
        assert -inf < []

        assert -inf <= -inf
        assert -inf <= inf
        assert -inf <= 0
        assert -inf <= 'a'
        assert -inf <= []

    def test_equalities(self):
        assert inf != -inf
        assert inf == inf
        assert -inf == -inf

    def test_infinities_are_singletons(self):
        assert _PInf() is _PInf()
        assert inf is _PInf()

        assert _NInf() is _NInf()
        assert -inf is _NInf()

        assert -(-inf) is inf

    def test_infinities_are_hashable(self):
        assert hash(inf) is not None
        assert hash(-inf) is not None
        assert hash(inf) != hash(-inf)
