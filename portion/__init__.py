from .api import create_api
from .const import Bound, inf
from .interval import Interval, AbstractDiscreteInterval
from .func import iterate, open, closed, openclosed, closedopen, empty, singleton
from .io import from_string, to_string, from_data, to_data
from .dict import IntervalDict


__all__ = [
    "create_api",
    "inf",
    "CLOSED",
    "OPEN",
    "Interval",
    "AbstractDiscreteInterval",
    "open",
    "closed",
    "openclosed",
    "closedopen",
    "singleton",
    "empty",
    "iterate",
    "from_string",
    "to_string",
    "from_data",
    "to_data",
    "IntervalDict",
]

CLOSED = Bound.CLOSED
OPEN = Bound.OPEN


# def _init():
#     # Create an API using our create_api machinery, and populate current
#     # module with the content of this API. We do this (rather than a classical
#     # import) so (1) we rely on our create_api function to ensure consistency
#     # in the exposed API, and (2) to preserve backward compatibility with
#     # versions prior to 2.4.0.
#     import sys

#     from .api import create_api
#     from .interval import Interval
#     from .dict import IntervalDict

#     _module = sys.modules[__name__]
#     _P = create_api(Interval, interval_dict=IntervalDict, name="P")

#     for name in _P.__all__:
#         setattr(_module, name, getattr(_P, name))
