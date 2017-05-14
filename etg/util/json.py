"""
A module for serializing different Python objects to JSON.
"""
import copy
import datetime
import json
from etg.simulation.energy import EnergyType, Producer
from etg.simulation.entity import Entity

def default(obj):
    """
    A convience method for JSON serializing some extra objects.
    """
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, EnergyType) or isinstance(obj, Entity):
        _dict = {}
        for key, value in obj.__dict__.items():
            if key == "simulation":
                pass
            else:
                _dict[key] = value
        return _dict
    elif isinstance(obj, Producer):
        return obj.__dict__
    else:
        raise TypeError("Object of type " + str(type(obj)) + " is not JSON serializable!")

def dumps(obj):
    """
    A convience function for dumping objects to JSON using our custom serializers.
    """
    return json.dumps(obj, default=default)
