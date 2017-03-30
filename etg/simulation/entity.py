"""
A generic superclass for all entities in the Energy Transistion Game, like
agents and companies.
"""

class Entity:
    def __init__(self, simulation):
        self.simulation = simulation
