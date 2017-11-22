********************
Running instructions
********************
These are the instructions for running the Energy Transition Game. Please make
sure you have :doc:`installed the etg <install>` first. Please make sure you
pick the same techincal level as you did when installing.

I want to run the game and do not know what I am doing
======================================================
1. Launch the python file `bin/start.py` by opening it with Python.
2. The game is now running!

I want to run the game and know that I am doing
===============================================
1. Open a terminal and change to the directory where you installed the game.
2. If you work with a virtual environment, activate it first::

        source venv/bin/activate

3. Run the following command::

        PYTHONPATH=".:$PYTHONPATH" twistd -ny bin/test-server

4. The game is now running!

I want to work on the game and know what I am doing
===================================================
See the instructions for running the game above.
