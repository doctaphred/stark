from collections import OrderedDict


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

    def __init__(self, initial):
        self._all = OrderedDict()
        for k, v in initial:
            self[k] = v

    def __getitem__(self, key, value):
        return self._all[key][-1]

    def getall(self, key):
        return self._all[key]

    def getindex(self, key, index):
        return self._all[key][index]

    def __setitem__(self, key, value):
        try:
            hist = self._all[key]
        except KeyError:
            self._all[key] = hist = []
        hist.append(value)

    def replace(self, key, value):
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
