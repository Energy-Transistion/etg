"""
A generic superclass for all entities in the Energy Transistion Game, like
agents and companies.
"""

class Entity:
    """
    The superclass for all other entities in the simulation.
    """
    def __init__(self, simulation):
        self.simulation = simulation

    def tick(self):
        """
        The actions that this entity should take during one of its steps.
        """
        pass
