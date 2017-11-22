"""
A module with specialized locks that allow us to make object read-only unless
the lock is locked.
"""
from threading import Lock

class ProxyException(Exception):
    """
    An exception to be throw when a user tries to alter the proxy or tries to
    call a function from the proxy
    """
    pass

class ProxyLock:
    """
    A class for creating lockable proxies. The proxy itself cannot be edited,
    and the proxied object can only be accessed by acquiering the lock.
    """

    # pylint: disable=too-few-public-methods

    __slots__ = ['_proxy', '_lock']

    def __init__(self, proxy):
        object.__setattr__(self, '_lock', Lock())
        object.__setattr__(self, '_proxy', proxy)

    def __getattribute__(self, attr):
        return ProxyLock(getattr(object.__getattribute__(self, '_proxy'), attr))

    def __delattr__(self, attr):
        raise ProxyException("Trying to delete the value {} on a ProxyLock".format(attr))

    def __setattr__(self, attr, value):
        raise ProxyException("Trying to set the value {} on a ProxyLock.".format(attr))

    def __call__(self, *args):
        raise ProxyException("Trying to call a ProxyLock. Acquire lock before calling")

    def __eq__(self, other):
        if isinstance(other, ProxyLock):
            return other == object.__getattribute__(self, '_proxy')
        else:
            return object.__getattribute__(self, '_proxy') == other

    def __enter__(self):
        object.__getattribute__(self, '_lock').acquire()
        return object.__getattribute__(self, '_proxy')

    def __exit__(self, exc_type, exc_value, traceback):
        object.__getattribute__(self, '_lock').release()

    # Borrowed from http://code.activestate.com/recipes/496741-object-proxying/
    _special_names = [
        '__abs__', '__add__', '__and__', '__cmp__', '__coerce__',
        '__contains__', '__delitem__', '__delslice__', '__div__', '__divmod__',
        '__float__', '__floordiv__', '__ge__', '__getitem__',
        '__getslice__', '__gt__', '__hash__', '__hex__', '__iadd__', '__iand__',
        '__idiv__', '__idivmod__', '__ifloordiv__', '__ilshift__', '__imod__',
        '__imul__', '__int__', '__invert__', '__ior__', '__ipow__', '__irshift__',
        '__isub__', '__iter__', '__itruediv__', '__ixor__', '__le__', '__len__',
        '__long__', '__lshift__', '__lt__', '__mod__', '__mul__', '__ne__',
        '__neg__', '__oct__', '__or__', '__pos__', '__pow__', '__radd__',
        '__rand__', '__rdiv__', '__rdivmod__', '__reduce__', '__reduce_ex__',
        '__repr__', '__reversed__', '__rfloorfiv__', '__rlshift__', '__rmod__',
        '__rmul__', '__ror__', '__rpow__', '__rrshift__', '__rshift__', '__rsub__',
        '__rtruediv__', '__rxor__', '__setitem__', '__setslice__', '__sub__',
        '__truediv__', '__xor__', 'next',
    ]

    @classmethod
    def _create_class_proxy(cls, theclass):
        """creates a proxy for the given class"""

        # pylint: disable=missing-docstring
        def make_method(name):
            # pylint: disable=missing-docstring
            def method(self, *args, **kw):
                return getattr(object.__getattribute__(self, "_proxy"), name)(*args, **kw)
            return method

        namespace = {}
        for name in cls._special_names:
            if hasattr(theclass, name):
                namespace[name] = make_method(name)
        return type("{}({})".format(cls.__name__, theclass.__name__), (cls,), namespace)

    def __new__(cls, obj, *args, **kwargs):
        """
        creates an proxy instance referencing `obj`. (obj, \*args, \*\*kwargs) are
        passed to this class' __init__, so deriving classes can define an
        __init__ method of their own.
        note: _class_proxy_cache is unique per deriving class (each deriving
        class must hold its own cache)
        """
        try:
            cache = cls.__dict__["_class_proxy_cache"]
        except KeyError:
            cls._class_proxy_cache = cache = {}
        try:
            theclass = cache[obj.__class__]
        except KeyError:
            cache[obj.__class__] = theclass = cls._create_class_proxy(obj.__class__)
        ins = object.__new__(theclass)
        theclass.__init__(ins, obj, *args, **kwargs)
        return ins
