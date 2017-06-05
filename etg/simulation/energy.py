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
    def __init__(self, simulation, name, color, greenness, safety, initial_output, initial_price,
                 tiers_unlocks, market_price):
        # pylint: disable=too-many-arguments
        super().__init__(simulation)
        self.name = name
        self.color = color
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
            return self.raw_price * (100 + self.simulation.active_party.taxes[self.name])/100
        except AttributeError:
            return 0

    @property
    def max_tier(self):
        """
        The maximum upgradeable tier for this energy type.
        """
        return len(self.tier_costs)

    @property
    def total_output(self):
        "The total amount of kWh that is produced and bought for this energy type"
        return sum(company.producers[self.name].output + company.market[self.name]
                   for company in self.simulation.companies)

    @property
    def percentage_use(self):
        "How large the percentage of the use of this type of energy is"
        total_production = sum(etype.total_output for etype in self.simulation.energy_types)
        if total_production == 0:
            return 0
        else:
            return self.total_output/total_production * 100

class Producer:
    """
    This class represents an energy producer in the game. It is used by the companies to keep track
    of their energy production.
    """
    # pylint: disable=too-few-public-methods,too-many-instance-attributes
    def __init__(self, energy_type):
        """
        :param energy_type: The energy type that this is a producer for.
        """
        self.tier = 0
        self.type = energy_type
        self.output = 0
        self.next_output = energy_type.initial_output
        self.price = 0
        self.sell_price = 0
        self.next_price = energy_type.initial_price
        self.upgrade_price = self.type.tier_costs[self.tier]
        self.color = energy_type.color

    @property
    def max_tier(self):
        """
        The max tier for this producer.
        """
        return self.type.max_tier

    def upgrade(self):
        """
        Upgrade the energy producer by one tier.
        """
        self.tier += 1
        self.output = self.next_output
        self.price = self.next_price
        if self.tier == self.type.max_tier:
            self.upgrade_price = None
        else:
            self.upgrade_price = self.type.tier_costs[self.tier]
        self.next_output += self.next_output / self.tier
        self.next_price /= 0.95
