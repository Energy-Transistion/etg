"""
A module for testing to make sure that the Handler collects the correct information.
"""
from twisted.trial import unittest
from etg.server.handler import Handler, Attribute
from etg.util.proxylock import ProxyLock

class Foo:
    """
    A class to test the Handler correctly updating the wrapee
    """
    # pylint: disable=too-few-public-methods
    def __init__(self, simulation, name, **kwargs):
        self.simulation = simulation
        self.name = name
        for key, val in kwargs.items():
            setattr(self, key, val)

class FooSimulation:
    """
    A class to test if the :class:`~etg.server.handler.Handler` correctly gets the correct
    information from the simulation.
    """
    # pylint: disable=too-few-public-methods
    def __init__(self, count=0, **kwargs):
        self.count = count
        for key, val in kwargs.items():
            setattr(self, key, val)

    def tick(self):
        """
        A small test method for ticking.
        """
        self.count += 1

class HandlerTestCase(unittest.TestCase):
    """
    A class to test the handler.
    """
    # pylint: disable=blacklisted-name,no-member,invalid-name,attribute-defined-outside-init

    def setUp(self):
        """
        A method to make all the objects necessary for testing.
        """
        self.simulation = FooSimulation(count=5, g=6, h=9, i=12)
        self.foo = Foo(simulation=self.simulation, name='foo', a=4, b=42, c="Hello")
        self.handler = Handler(ProxyLock(self.simulation),
                               ProxyLock(self.foo),
                               [Attribute("count"), Attribute("g")],
                               [Attribute("a"), Attribute('b')],
                               [Attribute('a')])

    def test_process_packet(self):
        """
        A test to see if the packets get processed correctly.
        """
        packet = {'a': 7}
        self.assertEqual(self.foo.a, 4)
        self.handler.process_packet(packet)
        self.assertEqual(self.foo.a, 7)
        packet = {'b': 9, 'a': 20}
        self.handler.process_packet(packet)
        self.assertEqual(self.foo.a, 20)
        self.assertEqual(self.foo.b, 42)

    def test_prepare_packet(self):
        """
        A test to make sure that the handler collects the right information.
        """
        self.handler.prepare_packet()
        self.foo.c = "World"
        self.foo.b = 21
        self.simulation.tick()
        packet = self.handler.prepare_packet()
        self.assertEqual(packet['b'], 21)
        self.assertEqual(packet['count'], 6)
        for key in ['g', 'c', 'a']:
            with self.assertRaises(KeyError):
                # pylint: disable=pointless-statement
                packet[key]
