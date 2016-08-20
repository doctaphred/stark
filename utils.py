"""Borrowed from phredutils"""

import weakref
from functools import wraps


def weak_cached(func):
    """Cache the function's return values with weak references.

    Once the decorated function has been called with a given set of
    args, it will return the same object for all subsequent calls, as
    long as another non-weak reference to the object still exists.
    """
    cache = weakref.WeakValueDictionary()

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return cache[args]
        except KeyError:
            cache[args] = result = func(*args, **kwargs)
            return result

    wrapper._cache = cache
    return wrapper


@weak_cached
def struct(*attrs):

    class Struct:

        names = attrs

        def __init__(self, *args, **kwargs):
            # asserts may be compiled away with the -O flag
            assert self.validate(*args, **kwargs) is None

            values = []
            positionals = iter(args)
            for name in self.names:
                try:
                    value = kwargs.pop(name)
                except KeyError:
                    value = next(positionals)
                values.append(value)

            super().__setattr__('values', tuple(values))
            super().__setattr__('items', tuple(zip(self.names, self.values)))
            super().__setattr__('_attrs', dict(self.items))

        def validate(self, *args, **kwargs):
            nargs = len(args)
            nkwargs = len(kwargs)

            if nargs + nkwargs != len(self.names):
                raise AttributeError(
                    'wrong number of args: got {} positional '
                    'and {} keyword; expected {} total'
                    .format(nargs, nkwargs, len(self.names)))

            invalid_kwargs = kwargs.keys() - set(self.names)
            if invalid_kwargs:
                raise AttributeError(
                    'invalid kwargs: {}'
                    .format(invalid_kwargs))

        def __getattr__(self, name):
            try:
                return self._attrs[name]
            except KeyError:
                raise AttributeError(name)

        def __setattr__(self, name, value):
            raise NotImplementedError

        def __delattr__(self, name):
            raise NotImplementedError

        def __iter__(self):
            return iter(self.values)

        def __len__(self):
            return len(self.values)

        def __eq__(self, other):
            return self.names == other.names and self.values == other.values

        def __hash__(self):
            return hash(self.values)

        def __repr__(self):
            reprs = ['{}={!r}'.format(k, v) for k, v in self.items]
            return '{}({})'.format(self.__class__.__name__, ', '.join(reprs))

    return Struct
