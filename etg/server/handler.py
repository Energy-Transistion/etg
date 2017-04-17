"""
This module contains all the code that is necessary to facilitate the updating
of the simulation and other objects from the interface, and also for sending
information back to the interface.
"""
from twisted.logger import Logger
from ..util.dict import difference

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
        self.simulation = simulation
        self.wrapee = wrapee
        self.name = wrapee.name
        self._state = {}
        self._viewables_simulation = view_simulation
        self._viewables_wrapee = view_wrapee
        self._controlables_wrapee = control_wrapee
        for key in self._viewables_wrapee:
            self._state[key] = None
        for key in self._viewables_simulation:
            self._state[key] = None
        self.prepare_packet()

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
                curstate[key] = getattr(wrapee, key)
        with self.simulation as simulation:
            for key in self._viewables_simulation:
                curstate[key] = getattr(simulation, key)
        diff = difference(self._state, curstate)
        return self._update_state(diff)

    def process_packet(self, packet):
        """
        Update the wrapee with all the values in the packet, if those values are controllable.

        :param dict packet: The values that need updating as a dictionary
        """
        with self.wrapee as wrapee:
            for key, val in packet.items():
                try:
                    if key in self._controlables_wrapee:
                        setattr(wrapee, key, val)
                except AttributeError as ex:
                    self._log.error("Trying to set a value that is not on the wrapee",
                                    exception=ex)
