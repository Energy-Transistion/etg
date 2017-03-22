"""
This module holds all of the networking code for the game. It has the following
submodules:

#. :mod:`.server`: This is the actual code for the server and it handles the
   webhosting and creating connections.
#. :mod:`.websocket`: This contains the code for creating and handling all the
   websocket based connections.
#. :mod:`.telnet`: This contains the code for creating and handling all the
   telnet based connections.
#. :mod:`.company`: This contains the code for updating the clients that are
   companies and making sure that events from these clients are handled in the
   simulation.
#. :mod:`.party`: This contains the code for updating the clients that are
   parties and making sure that events from these clients are handled in the
   simulation.
"""
