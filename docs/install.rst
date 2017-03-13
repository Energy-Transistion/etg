*************************
Installation instructions
*************************
These are the extended installation instructions for the Energy Transition 
Game. They are separated for the different needs and levels of technical 
insight. It is recommended that you pick the one that you are most comfortable 
with.

I want to run the game and know what I am doing
===============================================
1. Install a recent version of `Python 3`_. Version 3.6.0 should work fine.
2. Open a terminal and change to the directory where you downloaded the game.
3. Install the requirements in *base.txt* using the following command::

       pip3 install -r requirements/base.txt

4. You are now ready to run the game!

I want to work on the game and know what I am doing
===================================================
1. Install a recent version of `Python 3`_. Version 3.6.0 should work fine.
2. Open a terminal and change to the directory where you downloaded the game
3. [Optional] Create a new virtual environment::

       python3 -m venv venv

4. Activate the virtual environment::

       source venv/bin/activate

5. Install the requirements in *devel.txt* using the following command::

       pip install -r requirements/devel.txt

6. You are now ready to start work on the game!

Every time you start to work on the game, you need to run step 4 again.

.. _Python 3: https://www.python.org/downloads/
