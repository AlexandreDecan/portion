from .const import Bound
from .interval import Interval, singleton

from collections.abc import MutableMapping, Mapping


def _sort(i):
    return (i[0].lower, i[0].left is Bound.CLOSED, i[0].upper, i[0].right is Bound.OPEN)


class IntervalDict(MutableMapping):
    """
    An IntervalDict is a dict-like data structure that maps from intervals to data,
    where keys can be single values or Interval instances.

    When keys are Interval instances, its behaviour merely corresponds to
    range queries and it returns IntervalDict instances corresponding to the
    subset of values covered by the given interval. If no matching value is
    found, an empty IntervalDict is returned.
    When keys are "single values", its behaviour corresponds to the one of Python
    built-in dict. When no matchin value is found, a KeyError is raised.

    Note that this class does not aim to have the best performance, but is
    provided mainly for convenience. Its performance mainly depends on the
    number of distinct values (not keys) that are stored.
    """

    __slots__ = ('_items', )

    def __init__(self, mapping_or_iterable=None):
        """
        Return a new IntervalDict.

        If no argument is given, an empty IntervalDict is created. If an argument
        is given, and is a mapping object (e.g., another IntervalDict), an
        new IntervalDict with the same key-value pairs is created. If an
        iterable is provided, it has to be a list of (key, value) pairs.

        :param mapping_or_iterable: optional mapping or iterable.
        """
        self._items = list()  # List of (interval, value) pairs

        if mapping_or_iterable is not None:
            self.update(mapping_or_iterable)

    def clear(self):
        """
        Remove all items from the IntervalDict.
        """
        self._items.clear()

    def copy(self):
        """
        Return a shallow copy.

        :return: a shallow copy.
        """
        return IntervalDict(self)

    def get(self, key, default=None):
        """
        Return the values associated to given key.

        If the key is a single value, it returns a single value (if it exists) or
        the default value. If the key is an Interval, it returns a new IntervalDict
        restricted to given interval. In that case, the default value is used to
        "fill the gaps" (if any) w.r.t. given key.

        :param key: a single value or an Interval instance.
        :param default: default value (default to None).
        :return: an IntervalDict, or a single value if key is not an Interval.
        """
        if isinstance(key, Interval):
            d = self[key]
            d[key - d.domain()] = default
            return d
        else:
            try:
                return self[key]
            except KeyError:
                return default

    def find(self, value):
        """
        Return a (possibly empty) Interval i such that self[i] = value, and
        self[~i] != value.

        :param value: value to look for.
        :return: an Interval instance.
        """
        return Interval(*(i for i, v in self._items if v == value))

    def items(self):
        """
        Return a sorted list of (Interval, value) pairs.

        :return: a sorted list of 2-uples.
        """
        return sorted(self._items, key=_sort)

    def keys(self):
        """
        Return the list of underlying Interval instances.

        :return: a list of intervals.
        """
        return [i for i, v in self.items()]

    def values(self):
        """
        Return the list of values.

        :return: a list of values.
        """
        return [v for i, v in self.items()]

    def domain(self):
        """
        Return an Interval corresponding to the domain of this IntervalDict.

        :return: an Interval.
        """
        return Interval(*(i for i, v in self._items))

    def pop(self, key, default=None):
        """
        Return and remove given key.

        This method combines self[key] and del self[key]. If a default value
        is provided and is not None, it uses self.get(key, default) instead of
        self[key].

        :param key: a single value or an Interval instance.
        :param default: optional default value.
        :return: an IntervalDict, or a single value if key is not an Interval.
        """
        if default is None:
            value = self[key]
            del self[key]
            return value
        else:
            value = self.get(key, default)
            try:
                del self[key]
            except KeyError:
                pass
            return value

    def popitem(self):
        """
        Pop an arbitrary existing key.

        :return: an IntervalDict
        """
        try:
            return self.pop(self._items[-1][0])
        except IndexError:
            raise KeyError('Instance is empty.')

    def setdefault(self, key, default=None):
        """
        Return given key. If it does not exist, set its value to default and
        return it.

        :param key: a single value or an Interval instance.
        :param default: default value (default to None).
        :return: an IntervalDict, or a single value if key is not an Interval.
        """
        if isinstance(key, Interval):
            value = self.get(key, default)
            self.update(value)
            return value
        else:
            try:
                return self[key]
            except KeyError:
                self[key] = default
                return default

    def update(self, mapping_or_iterable):
        """
        Update current IntervalDict with provided values.

        If a mapping is provided, it must map Interval instances to values (e.g., another
        IntervalDict). If an iterable is provided, it must consist of a list of
        (key, value) pairs.

        :param mapping_or_iterable: mapping or iterable.
        """
        if isinstance(mapping_or_iterable, Mapping):
            data = mapping_or_iterable.items()
        else:
            data = mapping_or_iterable

        for i, v in data:
            i = singleton(i) if not isinstance(i, Interval) else i
            self[i] = v

    def __getitem__(self, key):
        if isinstance(key, Interval):
            items = []
            for i, v in self._items:
                intersection = key & i
                if not intersection.empty:
                    items.append((intersection, v))
            return IntervalDict(items)
        else:
            for i, v in self._items:
                if key in i:
                    return v
            raise KeyError(key)

    def combine(self, other, how):
        """
        Return a new IntervalDict that combines the values from current and
        provided ones.

        If d = d1.combine(d2, f), then d contains (1) all values from d1 whose
        keys do not intersect the ones of d2, (2) all values from d2 whose keys
        do not intersect the ones of d1, and (3) f(x, y) for x in d1, y in d2 for
        intersecting keys.

        :param other: another IntervalDict instance.
        :param how: a function of two parameters that combines values.
        :return: a new IntervalDict instance.
        """
        new_items = []

        dom1, dom2 = self.domain(), other.domain()

        new_items.extend(self[dom1 - dom2].items())
        new_items.extend(other[dom2 - dom1].items())

        intersection = dom1 & dom2
        d1, d2 = self[intersection], other[intersection]

        for i1, v1 in d1.items():
            for i2, v2 in d2.items():
                if i1.overlaps(i2):
                    i = i1 & i2
                    v = how(v1, v2)
                    new_items.append((i, v))

        return IntervalDict(new_items)

    def __setitem__(self, key, value):
        interval = key if isinstance(key, Interval) else singleton(key)

        if interval.empty:
            return

        new_items = []
        found = False
        for i, v in self._items:
            if value == v:
                found = True
                new_items.append((i | interval, v))
            elif i.overlaps(interval):
                remaining = i - interval
                if not remaining.empty:
                    new_items.append((remaining, v))
            else:
                new_items.append((i, v))

        if not found:
            new_items.append((interval, value))

        self._items = new_items

    def __delitem__(self, key):
        interval = key if isinstance(key, Interval) else singleton(key)

        if interval.empty:
            return

        new_items = []
        found = False
        for i, v in self._items:
            if i.overlaps(interval):
                found = True
                remaining = i - interval
                if not remaining.empty:
                    new_items.append((remaining, v))
            else:
                new_items.append((i, v))

        self._items = new_items

        if not found and not isinstance(key, Interval):
            raise KeyError(key)

    def __iter__(self):
        return iter(self.keys())

    def __len__(self):
        return len(self._items)

    def __contains__(self, key):
        return key in self.domain()

    def __repr__(self):
        return '{}{}{}'.format(
            '{',
            ', '.join('{!r}: {!r}'.format(i, v) for i, v in self.items()),
            '}',
        )

    def __eq__(self, other):
        if isinstance(other, IntervalDict):
            return self.items() == other.items()
        else:
            return NotImplemented
