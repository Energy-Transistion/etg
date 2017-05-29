"""
All the classes and methods having to do with the political parties in the game.
"""
import math
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

    def __init__(self, simulation, config, name):
        super(Party, self).__init__(simulation)
        self.name = name
        self.money = config['starting_money']
        self.taxes = {}
        for energy_type in self.simulation.energy_types:
            self.taxes[energy_type.name] = 0
        self.campaign_cost = config['campaign_cost']
        self._last_campaign = self.simulation.current_tick

    @property
    def voters(self):
        """
        All the voters for this party, as an :class:`~etg.util.agentset.AgentSet`.
        """
        return self.simulation.agents.filter(lambda a: a.party == self)

    @property
    def percentage_voters(self):
        """
        The percentage of the population that would vote for this party in the last poll, as a
        percentage.
        """
        try:
            return self.simulation.votes[self.name] * 100 / \
                (sum(self.simulation.votes[name] for name in self.simulation.votes) +
                 self.simulation.non_voters)

    @property
    def greenness(self):
        """
        The greenness of the policies of this party.
        """
        total_taxes = sum(self.taxes[k] for k in self.taxes)
        if total_taxes == 0:
            total_taxes = 1
        return sum(etype.greenness * self.taxes[etype.name] / total_taxes
                   for etype in self.simulation.energy_types)

    @property
    def safety(self):
        """
        The safeness of the policies of this party.
        """
        total_taxes = sum(self.taxes[k] for k in self.taxes)
        if total_taxes == 0:
            total_taxes = 1
        return sum(etype.safety * self.taxes[etype.name] / total_taxes
                   for etype in self.simulation.energy_types)

    def campaign(self):
        """
        The party can campaign in order to get more voters to vote for them. It then does need the
        required amount of money before it can start.
        """
        if self.money >= self.campaign_cost:
            self.money -= self.campaign_cost
            self._last_campaign = self.simulation.current_tick
            return True, ''
        else:
            return False, "Not enough money"

    def receive_donation(self, amount):
        """
        The party received a donation.
        """
        self.money += amount

    def tick(self):
        """
        In a turn, the party campaigns to get more voters.
        """
        percentage = 83 * math.exp((self._last_campaign - self.simulation.current_tick)/30)
        for agent in self.simulation.agents.n_of(int(percentage * len(self.simulation.agents))):
            agent.need_green = (agent.need_green * 100 + self.greenness * 0.10)/100
            agent.need_safety = (agent.need_safety * 100 + self.safety * 0.10)/100
