"""
The code for the server.
"""
import random
from etg.server.site import ETGSite
from etg.server.websocket import WebSocketConnection
from autobahn.twisted.websocket import WebSocketServerFactory
from autobahn.twisted.resource import WebSocketResource
from twisted.application import service, strports
from twisted.internet import task
from twisted.logger import Logger
from twisted.web.server import Site

log = Logger("etg.service")

class SimulationService(service.Service):
    """
    The Service that runs and keeps track of the simulation. It takes care of
    stepping through the simulation and handling all the new connections.
    """
    def __init__(self, simulation, options):
        self._simulation = simulation
        self.options = options
        self.paused = True
        self.is_setup = False
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

    def chat_all(self, message, source):
        """
        Send a chat message to all connected clients.
        """
        for prot in self.protocols:
            prot.send_chat(message, source, prot.name)

    def start(self):
        """
        Unpauze the server.
        """
        self.paused = False
        log.info("Started the simulation")
        return True, ''

    def pause(self):
        """
        Pauze the server.
        """
        self.paused = True
        log.info("Paused the simulation")
        return True, ''

    def toggle_pause(self):
        """
        This methods toggles wether the simulation, and thus the server, is paused.
        """
        self.paused = not self.paused
        log.info("Toggled the running state")

    def setup(self):
        """
        Sets up the simulation to make sure we can run.
        """
        if len(self.simulation.parties) < 1:
            return False, 'Not enough parties connected'
        elif len(self.simulation.companies) < 1:
            return False, 'Not enough companies connected'
        with self.simulation as simulation:
            simulation.election()
            simulation.active_party = random.choice(simulation.parties)
            for agent in simulation.agents:
                agent.use_deliberation()
        self.is_setup = True
        return True, ''

    def loop(self):
        """
        Run every step for the server once. Meant to be called repeatedly.
        """
        if not self.paused:
            with self.simulation as simulation:
                if simulation.active_party is None:
                    simulation.election()
                news = simulation.tick()
                if simulation.current_date.weekday() == 0:
                    voters, non_voters = simulation.poll()
                    log.info("Poll results in: % non voters: {non_voters}, votes: {votes}",
                             non_voters=non_voters, voters=voters)
            for protocol in self.protocols:
                protocol.send_packet()
                for new in news:
                    protocol.send_news(new)

def make_errback(server, _log=log):
    """
    Define an errback function to use for this service.
    """
    def errback(failure):
        """
        The function that gets called on errors.
        """
        server.pause()
        _log.error("Got a failure of type {type}.\n{traceback}",
                   type=failure.type, traceback=failure.getTraceback())
    return errback

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
    loop = task.LoopingCall(server.loop)
    loop_deferred = loop.start(simulation.tick_rate)
    loop_deferred.addErrback(make_errback(server, log))

    import socket
    ip_addr = socket.gethostbyname(socket.gethostname())
    print("Ask players to go to the following URL: http://{}:8080".format(str(ip_addr)))
    print("You can find the Admin interface at http://{}:8080/admin.html".format(str(ip_addr)))
    return application
