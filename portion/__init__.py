from importlib.metadata import version

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

__version__ = version("portion")
