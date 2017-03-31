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
        return object.__getattribute__(self, '_proxy') == other

    def __enter__(self):
        object.__getattribute__(self, '_lock').acquire()
        return object.__getattribute__(self, '_proxy')

    def __exit__(self, exc_type, exc_value, traceback):
        object.__getattribute__(self, '_lock').release()
