"""
All the classes and methods having to do with the companies in the game.
"""
from .entity import Entity
from .energy import Producer

class Company(Entity):
    """
    A class to represent the companies in the simulation. It contains
    information about the state of the company (funds, suppliers, consumers,
    etc) and methods for updating the company and validating user input. The
    companies are created when a player joins, and should not be created
    manually.
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, simulation, options, name):
        super(Company, self).__init__(simulation)
        self.set_values(options)
        self.name = name

    def set_values(self, config):
        """
        Set all the values on this company by coping them from the config dict
        from the simulation.
        """
        self.budget = config['starting_money']
        self.producers = {}
        self.market = {}
        for etype in self.simulation.energy_types:
            self.producers[etype.name] = Producer(etype)
            self.market[etype.name] = 0
        self.marketing = 0
        self.price = 0

    @property
    def users(self):
        """
        All the users of this comapny, as an :class:`~etg.util.agentset.AgentSet`.
        """
        return self.simulation.agents.filter(lambda a: a.company == self)

    @property
    def buyers(self):
        """
        The number of users of this company.
        """
        return len(self.users)

    @property
    def profit(self):
        """
        How much profit the company makes each tick.
        """
        return sum(agent.energy_consumed * self.price for agent in self.users) - self.rawcost

    @property
    def income(self):
        """
        How much money the company earned this tick.
        """
        return self.profit * (1 - self.marketing)

    @property
    def rawcost(self):
        """
        How much the product of the company costs the company itself.
        """
        return sum(self.market[etype.name] * etype.market_price
                   for etype in self.simulation.energy_types)

    @property
    def output(self):
        """
        The output of this company on the current tick.
        """
        return sum(self.producers[etype.name].output + self.market[etype.name]
                   for etype in self.simulation.energy_types)

    @property
    def product_green(self):
        """
        How green the product of this company is.
        """
        return sum(etype.greenness / self.output *
                   (self.producers[etype.name].output + self.market[etype.name])
                   for etype in self.simulation.energy_types)

    @property
    def product_safety(self):
        """
        How safe the product of this company is.
        """
        return sum(etype.safety / self.output *
                   (self.producers[etype.name].output + self.market[etype.name])
                   for etype in self.simulation.energy_types)

    @property
    def taxes(self):
        """
        The amount of taxation that goes over this product, calculated by taking the proportions for
        all the energy types in the output.
        """
        return sum((self.simulation.active_party.taxes[etype.name]/100) / self.output *
                   (self.producers[etype.name].output + self.market[etype.name])
                   for etype in self.simulation.energy_types)

    @property
    def product_cost(self):
        """
        How much the product from this company costs.
        """
        return self.price * self.taxes

    def donate(self, party_name, amount):
        """
        Donate the `amount` to the party with `party_name`. Returns `True` if succesful, `False`
        with an error message otherwise.
        """
        parties = list(filter(lambda p: p.name == party_name, self.simulation.parties))
        if len(parties) != 1:
            return False, "No or multiple parties with name {}".format(party_name)
        party = parties[0]
        if self.budget < amount:
            return False, "Not enough budget"
        self.budget -= amount
        party.money += amount
        return True, ""

    def tick(self):
        """
        In a tick, the companies do their marketing, by updating the needs of the agents to mimic
        their product.
        """
        self.budget += self.income
        for agent in self.simulation.agents:
            agent.need_green = (agent.need_green * 100 + self.product_green * self.marketing)/100
            agent.need_safety = (agent.need_safety * 100 + self.product_safety * self.marketing)/100
