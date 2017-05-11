"""
This module contains all the code for keeping track of the different energy types.
"""
from ..util.math import mean

class EnergyType:
    """
    This class represents a specific energy type, that is read in from a yaml file.
    """
    # pylint: disable=too-few-public-methods
    def __init__(self, simulation, name, greenness, safety, initial_output, tiers, market_price):
        # pylint: disable=too-many-arguments
        self.simulation = simulation
        self.name = name
        self.greenness = greenness
        self.safety = safety
        self.initial_output = initial_output
        self.tier_costs = tiers
        self.market_price = market_price

    @property
    def price(self):
        """
        The average price for this energy type.
        """
        return mean(company.producers[self.name].output * company.product_cost /
                    sum(producer.output for _, producer in company.producers.items())
                    for company in self.simulation.companies)

class Producer:
    """
    This class represents an energy producer in the game. It is used by the companies to keep track
    of their energy production.
    """
    def __init__(self, energy_type):
        """
        :param energy_type: The energy type that this is a producer for.
        """
        self.tier = 0
        self.type = energy_type
        self.output = 0
        self.next_output = energy_type.initial_output

    @property
    def upgrade_price(self):
        """
        The upgrade price that needs to be payed to upgrade this producer a tier, or None if already
        at the highest tier.
        """
        try:
            return self.type.tier_costs[self.tier]
        except IndexError:
            return None

    def upgrade(self):
        """
        Upgrade the energy producer by one tier.
        """
        self.tier += 1
        self.output = self.next_output
        self.next_output += self.next_output / self.tier
