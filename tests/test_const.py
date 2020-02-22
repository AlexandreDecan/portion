from intervals.const import inf, _PInf, _NInf, CLOSED, OPEN


class TestBounds:
    def test_complement(self):
        assert OPEN != CLOSED
        assert not OPEN == CLOSED
        assert not CLOSED == OPEN


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
