"""
Test to make sure that the proxylock works as it should.
"""
from twisted.trial import unittest
from etg.util.proxylock import ProxyLock, ProxyException

class Foo:
    """
    A quick class for testing the ProxyLock
    """

    # pylint: disable=too-few-public-methods,invalid-name,missing-docstring

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def foobar(self):
        return self.a + self.b

class ProxyTestCase(unittest.TestCase):
    """
    Testing functions for the proxy lock.
    """
    # pylint: disable=blacklisted-name, assigning-non-slot
    def test_proxy(self):
        """
        Test if the proxy allows acces to values, but does not allow us to set them
        """
        foo = Foo(4, 42)
        proxy = ProxyLock(foo)
        self.assertEqual(proxy.a, 4)
        self.assertEqual(proxy.b, 42)
        with self.assertRaises(ProxyException):
            proxy.foobar()
        with self.assertRaises(ProxyException):
            proxy.a = 5
            self.assertNotEqual(proxy.a, 5)

    def test_context_manager(self):
        """
        Test if the proxy works properly as a context manager
        """
        foo = Foo(4, 42)
        proxy = ProxyLock(foo)
        with proxy as value:
            value.b = 64
            value.a *= 5
            self.assertEqual(value.a, 20)
            self.assertEqual(value.b, 64)
        self.assertEqual(proxy.a, 20)
        self.assertEqual(proxy.b, 64)
