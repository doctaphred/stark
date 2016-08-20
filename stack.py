import pp


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

    def __getitem__(self, key):
        """Return the first match, from the top of the stack down."""
        for d in reversed(self.frames):
            try:
                return d[key]
            except KeyError:
                pass
        # TODO: add frames to the exception message
        pp(self.frames)
        raise KeyError(key)

    def __setitem__(self, key, value):
        """Set the key in the topmost namespace."""
        self.top[key] = value

    def __delitem__(self, key):
        """Delete the key from the topmost namespace."""
        del self.top[key]
