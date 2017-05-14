"""
A module for storing utility math functions.
"""
def mean(data):
    """
    Calculate the average value in a numeric list
    """
    _data = list(data)
    length = len(_data)
    if length > 0:
        return sum(_data)/length
    else:
        return 0
