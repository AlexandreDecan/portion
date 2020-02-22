class _Singleton():
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(_Singleton, cls).__new__(cls, *args, **kwargs)
        return cls.__instance


class _PInf(_Singleton):
    """
    Represent positive infinity.
    """

    def __neg__(self): return _NInf()

    def __lt__(self, o): return False

    def __le__(self, o): return isinstance(o, _PInf)

    def __gt__(self, o): return not isinstance(o, _PInf)

    def __ge__(self, o): return True

    def __eq__(self, o): return isinstance(o, _PInf)

    def __repr__(self): return '+inf'

    def __hash__(self): return hash(float('+inf'))


class _NInf(_Singleton):
    """
    Represent negative infinity.
    """

    def __neg__(self): return _PInf()

    def __lt__(self, o): return not isinstance(o, _NInf)

    def __le__(self, o): return True

    def __gt__(self, o): return False

    def __ge__(self, o): return isinstance(o, _NInf)

    def __eq__(self, o): return isinstance(o, _NInf)

    def __repr__(self): return '-inf'

    def __hash__(self): return hash(float('-inf'))


# Positive infinity
inf = _PInf()

# Boundary types (True for inclusive, False for exclusive)
CLOSED = True
OPEN = False
