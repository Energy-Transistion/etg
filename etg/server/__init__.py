"""
This module holds all of the networking code for the game. It has the following 
submodules:

#. :doc:`server`: This is the actual code for the server and it handles the 
   webhosting and creating connections.
#. :doc:`websocket`: This contains the code for creating and handling all the
   websocket based connections.
#. :doc:`telnet`: This contains the code for creating and handling all the 
   telnet based connections.
#. :doc:`company`: This contains the code for updating the clients that are
   companies and making sure that events from these clients are handled in the
   simulation.
#. :doc:`party`: This contains the code for updating the clients that are
   parties and making sure that events from these clients are handled in the
   simulation.
"""
