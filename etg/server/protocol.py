"""
This module implements the Protocol that is used by the server to communicate with the clients. This
code is independent of the actual networking code, so it can be used by multiple types of
connections.
"""
import html
from twisted.logger import Logger
from etg.util.proxylock import ProxyLock
from .handler import Handler, AdminHandler

# pylint: disable=invalid-name
log = Logger()

class ETGProtocol:
    """
    The actual protocol class. Every new connection should create one of these to handle all the
    communication logic.
    """
    party_watchers = (["current_date", "next_election", "active_party", "government_budget",
                       "government_income", "non_voters", "weather"],
                      ["money"],
                      ["taxes"])
    company_watchers = (["current_date", "next_election", "active_party", "parties", "weather"],
                        ["budget", "producers"],
                        ["marketing", "price", "market"])
    def __init__(self, service, simulation, connection):
        """
        :param service: The service parent of this Protocol, most likely an instance of
                        :class:`~etg.server.simulation`.
        :param simulation: The simulation that this Protocol talks about.
        :param connection: The 'connection' that reply messages get send over. Needs a `sendMessage`
                        method.
        """
        self.service = service
        self.simulation = simulation
        self.connection = connection
        self.handler = None
        self.name = ""

    def on_connection(self, name):
        """
        This method should be called whenever a new connection is made, and it should then be passed
        the name of the client, which the client should send on its first connection.
        """
        if name == "admin":
            self.name = "admin"
            self.handler = AdminHandler(self.service, self.simulation)
            return True
        parties = list(filter(lambda p: p.name == name, self.simulation.parties))
        if len(parties) == 1:
            self.handler = Handler(self.simulation, ProxyLock(parties[0]), self.party_watchers[0],
                                   self.party_watchers[1], self.party_watchers[2])
        else:
            companies = list(filter(lambda c: c.name == name, self.simulation.companies))
            if len(companies) == 1:
                self.handler = Handler(self.simulation, ProxyLock(companies[0]),
                                       self.company_watchers[0], self.company_watchers[1],
                                       self.company_watchers[2])
            else:
                self.connection.error("No company/party with name {}!".format(name))
                return False
        self.name = name
        self.send_packet(msg_type="initial")
        return True

    def on_message(self, message):
        """
        This method should be called whenever a message is received. this methods will then make
        sure that the message is handled properly.
        """
        log.info("Got message {message}", message=message)
        if message['type'] == "change":
            self.handler.process_packet(message['packet'])
            self.send_packet()
        elif message['type'] == "chat":
            self.on_chat_message(message)
        elif message['type'] == "action":
            self.on_action(message)
        elif message['type'] == "admin":
            if message['value'] == 'start':
                self.service.start()
                print("Starting server")
            elif message['value'] == 'setup':
                with self.simulation as simulation:
                    simulation.election()
                    for agent in simulation.agents:
                        agent.use_deliberation()
            else:
                self.service.pause()
                print("pausing server")
        else:
            log.warn("Unrecognized message type {type}", type=message['type'])

    def on_chat_message(self, message):
        """
        This message makes sure that the correct respondent gets the chat message if it is recieved.
        """
        if message['target'] == []:
            self.service.chat_all(message['text'], self.name)
        else:
            for target in self.service.protocols.filter(lambda p: p.name in message['target']):
                target.send_chat(message['text'], self.name)
            self.send_chat(message['text'], self.name)

    def send_chat(self, text, sender):
        """
        Send a chat message to this client.
        """
        self.connection.send({'type': 'chat', 'sender': sender, 'text': html.escape(text)})

    def on_action(self, message):
        """
        This method deals with new and income information and calls the corresponding method on the
        object.
        """
        try:
            with self.handler.wrapee as wrapee:
                func = getattr(wrapee, message['action'])
                func(*message['args'])
                self.send_packet()
        except AttributeError as e:
            log.warn("Trying to call a method {method} that does not exsist!", method=e.args[0])

    def send_news(self, msg):
        """
        Send a news message to the accompanying client.
        """
        self.connection.send({'type': 'news', 'news': str(msg)})

    def send_packet(self, msg_type='change'):
        """
        Prepare and send a packet to the client.
        """
        packet = self.handler.prepare_packet()
        self.connection.send({'type': msg_type, 'packet': packet})
