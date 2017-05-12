"""
The code for the server.
"""
from etg.server.site import ETGSite
from etg.server.websocket import WebSocketConnection
from autobahn.twisted.websocket import WebSocketServerFactory
from autobahn.twisted.resource import WebSocketResource
from twisted.application import service, strports
from twisted.web.server import Site

class SimulationService(service.Service):
    """
    The Service that runs and keeps track of the simulation. It takes care of
    stepping through the simulation and handling all the new connections.
    """
    def __init__(self, simulation, options):
        self._simulation = simulation
        self.options = options
        self.pauzed = True
        self.protocols = []

    @property
    def simulation(self):
        """
        The simulation that this simulation is about.
        """
        return self._simulation

    @property
    def parties(self):
        """
        A list with all the parties in the simulation.
        """
        return self._simulation.parties

    @property
    def companies(self):
        """
        A list with all the companies in the simulation.
        """
        return self._simulation.companies

    def add_protocol(self, protocol):
        """
        Add a new protocol to the service.
        """
        self.protocols.append(protocol)

    def remove_protocol(self, protocol):
        """
        Remove a protocol from the service.
        """
        self.protocols.remove(protocol)

    def get_websocket_factory(self):
        """
        Returns a factory to be used for WebSocket connections.
        """
        factory = WebSocketServerFactory(u"ws://127.0.0.1:8080")
        factory.protocol = WebSocketConnection
        factory.service = self
        factory.simulation = self.simulation
        return factory

    def get_telnet_factory(self):
        """
        Returns a factory to be used for telnet connections.
        """
        pass

    def make_site(self):
        """
        Sets up the site and returns it as a :class:`etg.server..site.ETGSite`.
        """
        site = ETGSite(self.options['site'], self)
        site.putChild(b"ws", WebSocketResource(self.get_websocket_factory()))
        return site

    def start(self):
        """
        Unpauze the server.
        """
        self.pauzed = False

    def pauze(self):
        """
        Pauze the server.
        """
        self.pauzed = True

    def toggle_pauze(self):
        """
        This methods toggles wether the simulation, and thus the server, is pauzed.
        """
        self.pauzed = not self.pauzed

def make_application(simulation, options):
    """
    Setup the server so it can be started with twistd.
    """
    application = service.Application('etg')
    service_collection = service.IServiceCollection(application)
    server = SimulationService(simulation, options)
    server.setServiceParent(service_collection)
    site = server.make_site()
    strports.service("tcp:8080", Site(site)).setServiceParent(service_collection)
    return application
