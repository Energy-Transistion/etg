"""
A testing suite for the dictionary utility functions.
"""
import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import etg.util.dict as d

def test_difference():
    """
    A test to see if the difference function works correctly
    """
    assert d.difference({'a': 'a', 'b': 'b'}, {'a':'a', 'b':'b'}) == {}
    assert d.difference({'a': 'c', 'b': 'b'}, {'a':'a', 'b':'b'}) == {'a': 'a'}
    assert d.difference({'c': 'c', 'b': 'b'}, {'a':'a', 'b':'d'}) == {'b': 'd'}

def test_difference_epsilon():
    """
    A test to see if the difference correctly taske into account the difference
    between two numbers.
    """
    assert d.difference({'a': 2.5, 'b': 3}, {'a':2.6, 'b':2.95}, 0.06) == {'a':2.6}
