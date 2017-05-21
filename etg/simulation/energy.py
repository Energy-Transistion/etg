"""
This module contains all the code for keeping track of the different energy types.
"""
from ..util.math import mean
from .entity import Entity

class EnergyType(Entity):
    """
    This class represents a specific energy type, that is read in from a yaml file.
    """
    # pylint: disable=too-few-public-methods, too-many-instance-attributes
    def __init__(self, simulation, name, greenness, safety, initial_output, initial_price,
                 tiers_unlocks, market_price):
        # pylint: disable=too-many-arguments
        super().__init__(simulation)
        self.name = name
        self.greenness = greenness
        self.safety = safety
        self.initial_output = initial_output
        self.initial_price = initial_price
        self.tier_costs = tiers_unlocks
        self.market_price = market_price

    @property
    def raw_price(self):
        """
        The average price for this energy type.
        """
        try:
            return mean(company.producers[self.name].output * company.price /
                        sum(producer.output for _, producer in company.producers.items())
                        for company in self.simulation.companies)
        except AttributeError:
            return 0

    @property
    def price(self):
        """
        The average price for this energy type including taxes.
        """
        try:
            return self.raw_price * self.simulation.active_party.taxes[self.name]
        except AttributeError:
            return 0

class Producer:
    """
    This class represents an energy producer in the game. It is used by the companies to keep track
    of their energy production.
    """
    # pylint: disable=too-few-public-methods
    def __init__(self, energy_type):
        """
        :param energy_type: The energy type that this is a producer for.
        """
        self.tier = 0
        self.type = energy_type
        self.output = 0
        self.next_output = energy_type.initial_output
        self.price = 0
        self.next_price = energy_type.initial_price
        self.upgrade_price = self.type.tier_costs[self.tier]

    def upgrade(self):
        """
        Upgrade the energy producer by one tier.
        """
        self.tier += 1
        self.output = self.next_output
        self.price = self.next_price
        self.upgrade_price = self.type.tier_costs[self.tier]
        self.next_output += self.next_output / self.tier
        self.next_price /= 0.95
