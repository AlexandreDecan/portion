from .const import OPEN, CLOSED, inf
from .interval import Interval, open, closed, openclosed, closedopen, empty, singleton
from .func import iterate
from .io import from_string, to_string, from_data, to_data
from .dict import IntervalDict


__all__ = [
    'inf', 'CLOSED', 'OPEN',
    'Interval',
    'open', 'closed', 'openclosed', 'closedopen', 'singleton', 'empty',
    'iterate',
    'from_string', 'to_string', 'from_data', 'to_data',
    'IntervalDict',
]

__package__ = 'python-intervals'
__version__ = '2.0.0-pre1'
__licence__ = 'LGPL3'
__author__ = 'Alexandre Decan'
__url__ = 'https://github.com/AlexandreDecan/python-intervals'
__description__ = 'Python data structure and operations for intervals'
