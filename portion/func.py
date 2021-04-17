import operator
from functools import partial

from .const import inf


def iterate(interval, step, *, base=None, reverse=False):
    """
    Iterate on the (discrete) values of given interval.

    This function returns a (lazy) iterator over the values of given interval,
    starting from its lower bound and ending on its upper bound (if interval is
    not open). Each returned value merely corresponds to lower + i * step, where
    "step" defines the step between consecutive values.
    It also accepts a callable that is used to compute the next possible
    value based on the current one.

    When a non-atomic interval is provided, this function chains the iterators obtained
    by calling itself on the underlying atomic intervals.

    The values returned by the iterator can be aligned with a base value with the
    "base" parameter. This parameter must be a callable that accepts the lower bound
    of the (atomic) interval as input, and returns the first value that needs to be
    considered for the iteration.
    By default, the identity function is used. If reverse=True, then the upper bound
    will be passed instead of the lower one.

    :param interval: an interval.
    :param step: step between values, or a callable that returns the next value.
    :param base: a callable that accepts a bound and returns an initial value.
    :param reverse: set to True for descending order.
    :return: a lazy iterator.
    """
    if base is None:
        def base(x):
            return x

    exclude = operator.lt if not reverse else operator.gt
    include = operator.le if not reverse else operator.ge
    step = step if callable(step) else partial(operator.add, step)

    value = base(interval.lower if not reverse else interval.upper)
    if (value == -inf and not reverse) or (value == inf and reverse):
        raise ValueError("Cannot start iteration with infinity.")

    for i in interval if not reverse else reversed(interval):
        value = base(i.lower if not reverse else i.upper)

        while exclude(value, i):
            value = step(value)

        while include(value, i):
            yield value
            value = step(value)
