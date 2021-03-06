"""
This module implements the Protocol that is used by the server to communicate with the clients. This
code is independent of the actual networking code, so it can be used by multiple types of
connections.
"""
from twisted.logger import Logger
from etg.util.proxylock import ProxyLock
from .handler import (Handler, Attribute, ObjectAttribute, ListAttribute,
                      MultiAttribute, DictAttribute)

log = Logger()

class ETGProtocol:
    """
    The actual protocol class. Every new connection should create one of these to handle all the
    communication logic.
    """
    party_watchers = ([Attribute("current_date"), Attribute("days_until_election"),
                       ObjectAttribute("active_party", Attribute("name")),
                       Attribute("government_budget"), Attribute("change_government_budget"),
                       Attribute("government_income"), Attribute("change_government_income"),
                       Attribute("total_production"), Attribute("total_demand"),
                       Attribute("greenness"), Attribute("change_greenness"),
                       Attribute("non_voters"), Attribute("weather"), Attribute("approval_rate"),
                       ListAttribute("energy_types",
                                     MultiAttribute(Attribute("name"), Attribute("raw_price"),
                                                    Attribute("percentage_use"),
                                                    Attribute("color"), Attribute("price"))),
                       ListAttribute("parties", MultiAttribute(Attribute("name"),
                                                               Attribute("color"),
                                                               Attribute("percentage_voters"))),
                       ListAttribute("companies", MultiAttribute(Attribute("name")))],
                      [Attribute("money"), Attribute("campaign_cost"),
                       Attribute("campaign_reach")],
                      [Attribute("taxes")])

    company_watchers = ([Attribute("current_date"), Attribute("days_until_election"),
                         ObjectAttribute("active_party", Attribute("name")),
                         Attribute("weather"),
                         ListAttribute("parties",
                                       MultiAttribute(Attribute("name"), Attribute("taxes"))),
                         ListAttribute("companies", MultiAttribute(Attribute("name"),
                                                                   Attribute("income"),
                                                                   Attribute("color"),
                                                                   Attribute("market_share"),
                                                                   Attribute("product_green")))],
                        [Attribute("budget"), Attribute("income"), Attribute("output"),
                         Attribute("demand"),
                         ListAttribute("total_output", MultiAttribute(Attribute("name"),
                                                                      Attribute("color"),
                                                                      Attribute("output"))),
                         DictAttribute("producers",
                                       MultiAttribute(Attribute("tier"), Attribute("output"),
                                                      Attribute("color"),
                                                      ObjectAttribute("type",
                                                                      Attribute("market_price")),
                                                      Attribute("max_tier"),
                                                      Attribute("upgrade_price"),
                                                      Attribute("next_output"),
                                                      Attribute("price"),
                                                      Attribute("next_price"),
                                                      Attribute("sell_price")))],
                        [Attribute("marketing"), Attribute("price"), Attribute("market"),
                         DictAttribute("producers", MultiAttribute(Attribute("production_level")))])

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
            self.handler = Handler(self.simulation, ProxyLock(self.service),
                                   [Attribute("weather"), Attribute("current_date"),
                                    ListAttribute("parties",
                                                  MultiAttribute(Attribute("name"))),
                                    ListAttribute("companies",
                                                  MultiAttribute(Attribute("name"),
                                                                 Attribute("color"),
                                                                 Attribute("market_share"))),
                                    ListAttribute("energy_types",
                                                  MultiAttribute(Attribute("percentage_use"),
                                                                 Attribute("name"),
                                                                 Attribute("color")))],
                                   [Attribute("paused"), Attribute("is_setup")], [])
            self.send_packet(msg_type="initial")
            return True
        entity_type = ''
        parties = list(filter(lambda p: p.name == name, self.simulation.parties))
        if len(parties) == 1:
            self.handler = Handler(self.simulation, ProxyLock(parties[0]), self.party_watchers[0],
                                   self.party_watchers[1], self.party_watchers[2])
            entity_type = 'party'
        else:
            companies = list(filter(lambda c: c.name == name, self.simulation.companies))
            if len(companies) == 1:
                self.handler = Handler(self.simulation, ProxyLock(companies[0]),
                                       self.company_watchers[0], self.company_watchers[1],
                                       self.company_watchers[2])
                entity_type = 'company'
            else:
                self.connection.error("No company/party with name {}!".format(name))
                return False
        self.name = name
        self.send_packet(msg_type="initial")
        for protocol in self.service.protocols:
            protocol.send_packet()
            protocol.send_news("New {type} named {name} created!"\
                    .format(type=entity_type, name=name))
        return True

    def on_message(self, message):
        """
        This method should be called whenever a message is received. this methods will then make
        sure that the message is handled properly.
        """
        log.debug("Protocol got message {message}", message=message)
        if message['type'] == "change":
            self.handler.process_packet(message['packet'])
            self.send_packet()
        elif message['type'] == "chat":
            self.on_chat_message(message)
        elif message['type'] == "action":
            self.on_action(message)
        else:
            log.warn("Unrecognized message type {type}", type=message['type'])

    def on_chat_message(self, message):
        """
        This message makes sure that the correct respondent gets the chat message if it is recieved.
        """
        if message['target'] == '':
            self.service.chat_all(message['text'], self.name)
        else:
            targets = list(filter(lambda p: p.name == message['target'], self.service.protocols))
            print(targets)
            if len(targets) == 1:
                target = targets[0]
                target.send_chat(message['text'], self.name, target.name, whisper=True)
                if self.name != target.name:
                    self.send_chat(message['text'], self.name, target.name, whisper=True)
            else:
                log.warn("Trying to chat player {name}, but this player is not found!",
                         name=message['target'])

    def send_chat(self, text, sender, target, whisper=False):
        """
        Send a chat message to this client.
        """
        self.connection.send({'type': 'chat', 'sender': sender, 'target': target,
                              'text': text, 'whisper': whisper})

    def on_action(self, message):
        """
        This method deals with new and income information and calls the corresponding method on the
        object.
        """
        with self.handler.wrapee as wrapee:
            log.debug("Calling {method} on {name}", method=message['action'], name=self.name)
            try:
                func = getattr(wrapee, message['action'])
            except AttributeError as ex:
                log.warn("Trying to call a method {method} that does not exsist!",
                         method=ex.args[0])
                return
            res, msg = func(*message['args'])
        if not res:
            log.warn("Error while calling {method}: {msg}", msg=msg,
                     method=message['action'])
        else:
            log.debug("Called method succesfully")
            for protocol in self.service.protocols:
                protocol.send_packet()
                if msg != '':
                    protocol.send_news(msg)

    def send_news(self, msg):
        """
        Send a news message to the accompanying client.
        """
        log.debug("Sending news: {news}", news=msg)
        self.connection.send({'type': 'news', 'news': str(msg)})

    def send_packet(self, msg_type='change'):
        """
        Prepare and send a packet to the client.
        """
        packet = self.handler.prepare_packet()
        log.debug("Preparing to send packet for {name}", name=self.name)
        if packet and packet != {}:
            log.debug("Sending packet: {packet} to: {name}", packet=packet, name=self.name)
            self.connection.send({'type': msg_type, 'packet': packet})
