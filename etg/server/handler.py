"""
This module contains all the code that is necessary to facilitate the updating
of the simulation and other objects from the interface, and also for sending
information back to the interface.
"""
import copy
from twisted.logger import Logger
from ..util.dict import difference, merge

class Handler():
    """
    The `Handler` class makes sure that all the messages it recieves properly
    update the correspoding values in the wrapee and the simulation, in a
    threadsafe manner. It also gives convience methods for collection
    information that needs to be delivered to the interface.

    A new `Handler` has the following attributes:

    .. py:attribute:: simulation

        The simulation that the communication is about, as a
        :class:`etg.util.proxylock.ProxyLock`.

    .. py:attribute:: wrapee

        The object that needs updating from this simulation, as a
        :class:`etg.util.proxylock.ProxyLock`
    """

    _log = Logger()

    def __init__(self, simulation, wrapee, view_simulation, view_wrapee, control_wrapee):
        """
        To create a new handler, the simulation and the wrapee need to be
        specified. The initializer also needs a list with attributes that can
        be viewed on the simulation and the wrapee.

        :param ProxyLock simulation: A ProxyLock for the simulation
        :param ProxyLock wrapee: A ProxyLock for the object to wrap over
        :param list view_simulation: A list of attributes that are viewable on the simulation
        :param list view_wrapee: A list of attributes that are viewable on the wrapee
        :param list control_wrapee: A list with attributes that can be set on the wrapee
        """
        # pylint: disable=too-many-arguments
        self.simulation = simulation
        self.wrapee = wrapee
        self.name = wrapee.name
        self._state = {}
        self._viewables_simulation = view_simulation
        self._viewables_wrapee = view_wrapee
        self._controlables_wrapee = control_wrapee
        for key in self._viewables_wrapee:
            self._state[key.key] = None
        for key in self._controlables_wrapee:
            self._state[key.key] = None
        for key in self._viewables_simulation:
            self._state[key.key] = None

    def _update_state(self, new):
        """
        Update the state of the handler
        """
        self._state.update(new)
        return new

    def prepare_packet(self):
        """
        Collect the values that the server needs to send to the client.

        :return: All the values that have changed since the last call to this \
        function
        """
        curstate = {}
        with self.wrapee as wrapee:
            for key in self._viewables_wrapee:
                curstate[key.key] = copy.deepcopy(key.get(wrapee))
            for key in self._controlables_wrapee:
                value = copy.deepcopy(key.get(wrapee))
                if key.key in curstate:
                    curstate[key.key] = merge(curstate[key.key], value)
                else:
                    curstate[key.key] = value
        with self.simulation as simulation:
            for key in self._viewables_simulation:
                curstate[key.key] = copy.deepcopy(key.get(simulation))
        diff = difference(self._state, curstate)
        return self._update_state(diff)

    def process_packet(self, packet):
        """
        Update the wrapee with all the values in the packet, if those values are controllable.

        :param dict packet: The values that need updating as a dictionary
        """
        def make_equal(obj1):
            "Make a lambda that tests if two things are equal"
            return lambda a: a.key == obj1
        with self.wrapee as wrapee:
            for key, val in packet.items():
                try:
                    attrs = list(filter(make_equal(key), self._controlables_wrapee))
                    if len(attrs) > 0:
                        attr = attrs[0]
                        attr.set(wrapee, val)
                        self._log.info("Set the value for {key}", key=key)
                    else:
                        self._log.warn("Failed to set the value for {key}", key=key)
                except AttributeError as ex:
                    self._log.error("Trying to set a value that is not on the wrapee:\n{exception}",
                                    exception=ex)

class Attribute:
    """
    A class to represent one attribute on an object.
    """
    def __init__(self, attr):
        """
        :param attr: The attribute to get.
        """
        self.attr = attr

    def get(self, obj):
        """
        Get the value represented by this Attribute from an object.
        """
        return getattr(obj, self.attr)

    def set(self, obj, value):
        """
        Set the value represetned by this attribute on an object to `value`.
        """
        try:
            attr = self.get(obj)
            attr.update(value)
        except AttributeError:
            setattr(obj, self.attr, value)

    @property
    def key(self):
        """
        The property that this attribute is getting, so under which name it should be stored.
        """
        return self.attr

class ObjectAttribute(Attribute):
    """
    A class to represent an object from which we want multiple variables.
    """
    def __init__(self, attr, *attrs):
        super().__init__(attr)
        self.attrs = attrs

    def get(self, obj):
        ret = {}
        value = super().get(obj)
        if value is None:
            return {}
        for attr in self.attrs:
            ret[attr.attr] = attr.get(value)
        return ret

    def set(self, obj, value):
        obj2 = self.get(obj)
        for attr in self.attrs:
            try:
                attr.set(obj2, value[attr.key])
            except KeyError:
                pass

class ListAttribute(Attribute):
    """
    A class to represent an attribute that we want for all elements of a list.
    """
    def __init__(self, attr, value):
        super().__init__(attr)
        self.attrs = value

    def get(self, obj):
        ret = []
        value = super().get(obj)
        for val in value:
            ret.append(self.attrs.get(val))
        return ret

    def set(self, obj, value):
        obj2 = super().get(obj)
        for val in obj2:
            self.attrs.set(val, value)

class DictAttribute(Attribute):
    """
    A class to represent an attribute that we want for all elements of a dictionary.
    """
    def __init__(self, attr, value):
        super().__init__(attr)
        self.attrs = value

    def get(self, obj):
        ret = {}
        value = super().get(obj)
        for key in value:
            ret[key] = self.attrs.get(value[key])
        return ret

    def set(self, obj, value):
        obj2 = super().get(obj)
        for key in value:
            self.attrs.set(obj2[key], value[key])

class MultiAttribute(Attribute):
    """
    Get multiple values from one object.
    """
    # pylint: disable=super-init-not-called
    def __init__(self, *attrs):
        self.attrs = attrs

    def get(self, obj):
        ret = {}
        for attr in self.attrs:
            ret[attr.key] = attr.get(obj)
        return ret

    def set(self, obj, value):
        for attr in self.attrs:
            if attr.key in value:
                attr.set(obj, value[attr.key])
