import pytest

from intervals.const import inf,_PInf, _NInf


def test_infinity_comparisons():
    assert inf > -inf
    assert -inf < inf
    assert -inf != inf
    assert not (-inf == inf)


@pytest.mark.parametrize('inf', [inf, -inf])
def test_infinity_comparisons_with_self(inf):
    assert inf == inf
    assert inf >= inf
    assert inf <= inf
    assert not (inf > inf)
    assert not (inf < inf)
    assert not (inf != inf)


def test_infinities_are_singletons():
    assert _PInf() == _PInf()
    assert _PInf() is _PInf()
    assert _PInf() is -_NInf()

    assert _NInf() == _NInf()
    assert _NInf() is _NInf()

    assert _PInf() is not _NInf()
    assert _PInf() is not -_PInf()


@pytest.mark.parametrize('o', [0, 1, 1.0, 'a', list(), tuple(), dict()])
def test_infinity_comparisons_with_objects(o):
    assert o != inf and not (o == inf)
    assert o < inf and inf > o
    assert o <= inf and inf >= o

    assert o != -inf and not (o == -inf)
    assert o > -inf and -inf < o
    assert o >= -inf and -inf <= o


def test_infinities_are_hashable():
    assert hash(inf) is not None
    assert hash(-inf) is not None
    assert hash(inf) != hash(-inf)