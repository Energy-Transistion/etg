*************************
Installation instructions
*************************
These are the extended installation instructions for the Energy Transition
Game. They are separated for the different needs and levels of technical
insight. It is recommended that you pick the one that you are most comfortable
with, but do not forget to read the general notes first.

General Notes
=============
The first thing that you have to do is download the ETG on the `downloads
page`_. Here you can find all versions of the ETG collected together. Once you
have downloaded the version that you want, you should place the folder where
you want the installed game to go. One thing to note here is that the path to
this folder should not contain any spaces. This means that the name of none of
the folders above the ETG folder should contain a space.  So the path
`/Users/Rene/Documents/ETG/` is fine, but the path `/Users/Rene/My
Documents/ETG/` will lead to problems.

All the paths mentioned in the rest of the instructions are relative to the ETG
folder. So if you placed the ETG folder in `/Users/<username>/Documents/ETG`,
then you can find the file `bin/install.py` in
`/Users/<username>/Documents/ETG/bin/install.py`.

If you have any problems with installing or running the game, please check out
the `issues section` to see if someone had a similar problem. If your problem
is new, feel free to make a new issue there.

I want to run the game and do not know what I am doing
======================================================
1. Install a recent version of `Python 3`_. Version 3.6 should work fine.
2. If you use a Mac, open a terminal and copy the following command::

        xcode-select --install

3. Run the python file `bin/install.py` by opening it with Python.
4. You are ready to run the game!

I want to run the game and know what I am doing
===============================================
1. Install a recent version of `Python 3`_. Version 3.6.0 should work fine.
2. Open a terminal and change to the directory where you downloaded the game.
3. On a Mac, you will first have to install the xcode command line utilities
   with the following command::

        xcode-select --install

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
.. _downloads page: https://github.com/Energy-Transition/etg/releases
.. _issues section: https://github.com/Energy-Transition/etg/issues
