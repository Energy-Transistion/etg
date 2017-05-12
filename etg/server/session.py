"""
This module keeps track of different aspects of the state that the aplication needs
"""
from zope.interface import Interface, Attribute, implementer
from twisted.python.components import registerAdapter
from twisted.web.server import Session

class ISessionState(Interface):
    """
    An interface for specifying what the session state needs as a minimum.
    """
    name = Attribute("The name of the 'entity' (company/party) that is playing")
    short_name = Attribute("A shorthand for the 'entity'")
    player_name = Attribute("The name of the player")
    taxes = Attribute("The taxes that the party starts out with")

@implementer(ISessionState)
class SessionState(object):
    """
    The actual state for the session. Implements everything in
    :class:`~etg.server.session.ISessionState`
    """
    def __init__(self, session):
        self.name = ""
        self.short_name = ""
        self.player_name = ""

def get_session_state(request):
    """
    Returns the session state for a specific request, so it can be updated or read.
    """
    return ISessionState(request.getSession())

registerAdapter(SessionState, Session, ISessionState)
