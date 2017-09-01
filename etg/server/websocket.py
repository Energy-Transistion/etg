"""
A module for sending and recieving events over Websockets.
"""
import json
from autobahn.twisted.websocket import WebSocketServerProtocol
from twisted.logger import Logger
from etg.util.json import dumps as json_dump
from .protocol import ETGProtocol

log = Logger()

class WebSocketConnection(WebSocketServerProtocol):
    """
    The class that does all the reading and writing to and from the websockets.
    """
    def onOpen(self):
        """
        This method triggers once the connection is open, and creates the used ETGProtocol.
        """
        log.info("Opened new connection")
        self.protocol = ETGProtocol(self.factory.service, self.factory.simulation, Sender(self))
        self.factory.service.add_protocol(self.protocol)

    def onMessage(self, line, isBinary):
        """
        This method triggers once a new message is deliverd. It decodes the message and passes it on
        to the used protocol.
        """
        line = line.decode('utf-8')
        if self.protocol.name == "":
            if self.protocol.on_connection(line):
                log.info("Player {name} connected", name=self.protocol.name)
            else:
                log.warn("Player connected with name {name}, but this name does not exist",
                         name=line)
        else:
            log.debug("Got message {message}", message=line)
            self.protocol.on_message(json.loads(line))

    def onClose(self, wasClean, code, reason):
        try:
            name = self.protocol.name
            self.factory.service.remove_protocol(self.protocol)
        except AttributeError:
            name = ""
        log.info("Player {name} disconnected cleanly {clean} with code {code} and reason {reason}",
                 name=name, clean=wasClean, code=code, reason=reason)

class Sender:
    """
    The class that does all the translation from strings to bytes.
    """
    def __init__(self, connection):
        self.connection = connection

    def send(self, message):
        """
        Send an object over the underlying connection.
        """
        string = json_dump(message)
        log.info("Sending message {message}", message=message)
        self.connection.sendMessage(string.encode('utf-8'), isBinary=False)

    def error(self, message):
        """
        Send an error message over the underlying connection.
        """
        self.send({'type': 'error', 'error': message})
