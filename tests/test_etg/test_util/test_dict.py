"""
A testing suite for the dictionary utility functions.
"""
from twisted.trial import unittest
import etg.util.dict as d

class DictTestCase(unittest.TestCase):
    """
    Testing functions for all the dictionary functions.
    """
    def test_difference(self):
        """
        A test to see if the difference function works correctly
        """
        self.assertEqual(d.difference({'a': 'a', 'b': 'b'}, {'a':'a', 'b':'b'}), {})
        self.assertEqual(d.difference({'a': 'c', 'b': 'b'}, {'a':'a', 'b':'b'}), {'a': 'a'})
        self.assertEqual(d.difference({'c': 'c', 'b': 'b'}, {'a':'a', 'b':'d'}), {'b': 'd'})

    def test_difference_epsilon(self):
        """
        A test to see if the difference correctly taske into account the difference
        between two numbers.
        """
        self.assertEqual(d.difference({'a': 2.5, 'b': 3}, {'a':2.6, 'b':2.95}, 0.06), {'a':2.6})
