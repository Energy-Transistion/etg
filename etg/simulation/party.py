"""
All the classes and methods having to do with the political parties in the game.
"""
from .entity import Entity

class Party(Entity):
    """
    A class to represent the parties in the simulation. It contains
    information about the state of the party (funds, policies, voters,
    etc) and methods for updating the party and validating user input. The
    parties are created when a player joins, and should not be created
    manually.
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, simulation, name):
        super(Party, self).__init__(self, simulation)
        self.set_values(self.simulation.config['Parties'])
        self.name = name

    def set_values(self, config):
        """
        Set all the values on this party by coping them from the config dict
        from the simulation.
        """
        self.money = config['starting_money']
        self.tax_solar = config['tax_solar']
        self.tax_wind = config['tax_wind']
        self.tax_gas = config['tax_gas']
        self.tax_oil = config['tax_oil']
        self.tax_nuclear = config['tax_nuclear']
        self.tax_coal = config['tax_coal']

    @property
    def voters(self):
        """
        All the voters for this party, as an `~.agentset.AgentSet`.
        """
        return self.simulation.agents.filter(lambda a: a.party == self)

    @property
    def campaign(self):
        """
        How much is spend on campaigning in this tick.
        """
        pass

    @property
    def income(self):
        """
        How much money the company earned this tick.
        """
        pass
