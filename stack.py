from collections import OrderedDict
from itertools import chain

from utils import unique


class Frame:
    """An ordered dict of stacks.

    TODO: deques?

    >>> f = Frame([('x', 1), ('x', 2)])
    >>> f
    Frame([(x, [1, 2])])
    >>> f['x'] = 3
    >>> f
    Frame([(x, [1, 2, 3])])

    >>> f['x']
    3
    >>> f.get('x')
    3
    >>> f.getall('x')
    [1, 2, 3]
    >>> f.getindex('x', 0)
    1

    >>> list(f.keys())
    ['x']
    >>> list(f.values())
    [1]
    >>> list(f.items())
    >>> [('x', 1)]
    >>> list(f.allitems())
    >>> [('x', 1), ('x', 2), ('x', 3)]
    >>> f.pop('x')
    1
    >>> f.popall('x')
    [2, 3]
    """

    # TODO: use this instead of dicts in the Stack class below

    # TODO: implement __delitem__ by pushing a 'DELETED' sentry?

    def __init__(self, initial):
        self._all = OrderedDict()
        for k, v in initial:
            self[k] = v

    def __getitem__(self, key):
        """Return the present value of the key."""
        return self._all[key][-1]

    def getall(self, key):
        """Return all values, past and present, of the given key."""
        return self._all[key]

    def getindex(self, key, index):
        """Get the value of the key at a specific index.

        Negative indexing usually makes the most sense here.
        """
        return self._all[key][index]

    def __setitem__(self, key, value):
        """Update the present value of the key.

        The previous value is preserved in the key's history.
        """
        try:
            hist = self._all[key]
        except KeyError:
            self._all[key] = hist = []
        hist.append(value)

    def replace(self, key, value):
        """Replace the present value of the key.

        Returns the value that was replaced.
        """
        try:
            hist = self._all[key]
        except KeyError:
            self._all[key] = hist = []
        prev = hist.pop()
        hist.append(value)
        return prev

    def pop(self, key):
        return self._all[key].pop()

    def popall(self, key):
        return self._all.pop(key)

    def keys(self):
        return self._all.keys()

    def __iter__(self):
        return iter(self._all)


class Stack:
    """Basically a ChainMap."""

    def __init__(self, initial=None):
        if initial is None:
            initial = {}
        self.frames = [initial]

    @property
    def top(self):
        return self.frames[-1]

    def push(self, new=None):
        """Add a new namespace to the top of the stack."""
        if new is None:
            new = {}
        self.frames.append(new)

    def pop(self):
        """Remove the top namespace from the stack."""
        return self.frames.pop()

    def get(self, key, default):
        try:
            return self[key]
        except KeyError:
            return default

    def __getitem__(self, key):
        """Return the first match, from the top of the stack down."""
        for d in reversed(self.frames):
            try:
                return d[key]
            except KeyError:
                pass
        raise KeyError(key)

    def __setitem__(self, key, value):
        """Set the key in the topmost namespace."""
        self.top[key] = value

    def __delitem__(self, key):
        """Delete the key from the topmost namespace."""
        del self.top[key]

    def update(self, other):
        for k, v in other.items():
            self[k] = v
        # TODO: don't require .items?
        # for k in other:
        #     self[k] = other[k]

    def setdefault(self, key, default):
        if key not in self:
            self[key] = default

    def hoist(self, key):
        """Copy the key's value into the topmost frame."""
        self[key] = self[key]

    def keys(self):
        return set(self)

    def __iter__(self):
        yield from unique(chain.from_iterable(reversed(self.frames)))

    # TODO: __missing__?
