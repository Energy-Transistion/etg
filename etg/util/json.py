"""
A module for serializing different Python objects to JSON.
"""
import datetime
import json
from etg.simulation.energy import Producer
from etg.simulation.entity import Entity

def default(obj):
    """
    A convience method for JSON serializing some extra objects.
    """
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, Entity):
        _dict = {}
        for key in dir(obj):
            if key == "simulation" or key.startswith('__'):
                pass
            else:
                value = getattr(obj, key)
                if not callable(value):
                    _dict[key] = value
        return _dict
    elif isinstance(obj, Producer):
        return obj.__dict__
    else:
        print("Object of type " + str(type(obj)) + " is not JSON serializable!")
        return None

def dumps(obj):
    """
    A convience function for dumping objects to JSON using our custom serializers.
    """
    return json.dumps(obj, default=default)
