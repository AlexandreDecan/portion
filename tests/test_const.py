import hypothesis.strategies as st

from hypothesis import given, example
from intervals.const import inf, _PInf, _NInf, CLOSED, OPEN


class TestBounds:
    def test_complement(self):
        assert OPEN != CLOSED
        assert not OPEN == CLOSED
        assert not CLOSED == OPEN


class TestInfinities:
    @example(0)
    @example('a')
    @example([])
    @example(-inf)
    @given(st.one_of(st.integers(), st.booleans(), st.floats(), st.text()))
    def test_pinf_is_greater(self, v):
        assert inf > v
        assert not (inf < v)
        assert inf >= v
        assert not (inf <= v)

    def test_pinf_and_ninf(self):
        assert not (inf > inf)
        assert not (-inf < -inf)

    @example(0)
    @example('a')
    @example([])
    @example(inf)
    @given(st.one_of(st.integers(), st.booleans(), st.floats(), st.text()))
    def test_ninf_is_lower(self, v):
        assert -inf < v
        assert not (-inf > v)
        assert -inf <= v
        assert not (-inf >= v)

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
