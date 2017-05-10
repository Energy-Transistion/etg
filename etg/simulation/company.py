"""
All the classes and methods having to do with the companies in the game.
"""
from .entity import Entity

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
        self.money = config['starting_money']
        self.margin = config['margin']
        self.supplier_solar = config['supplier_solar']
        self.supplier_wind = config['supplier_wind']
        self.supplier_gas = config['supplier_gas']
        self.supplier_oil = config['supplier_oil']
        self.supplier_nuclear = config['supplier_nuclear']
        self.supplier_coal = config['supplier_coal']

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
        pass

    @property
    def marketing(self):
        """
        How much is spend on marketing in this tick.
        """
        pass

    @property
    def income(self):
        """
        How much money the company earned this tick.
        """
        pass

    @property
    def product_green(self):
        """
        How green the product of this company is.
        """
        pass

    @property
    def product_safety(self):
        """
        How safe the product of this company is.
        """
        pass

    @property
    def product_cost(self):
        """
        How much the product from this company costs.
        """
        pass

    @property
    def rawcost(self):
        """
        How much the product of the company costs the company itself.
        """
        pass

    def tick(self):
        """
        In a tick, the companies do their marketing, by updating the needs of the agents to mimic
        their product.
        """
        for agent in self.simulation.agents:
            agent.need_green = (agent.need_green * 100 + self.product_green * self.marketing)/100
            agent.need_safety = (agent.need_safety * 100 + self.product_safety * self.marketing)/100
