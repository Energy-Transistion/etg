"""
All classes and methods having to do with agents
"""
from random import choice, random, randrange, normalvariate, uniform
import math
from ..util.agentset import AgentSet
from ..util.math import mean
from .entity import Entity

class Agent(Entity):
    """
    A class to represent a single agent in the artificial population. It
    contains information about the state of the agent (income, certainness,
    friends, etc) and methods for updating the agent on each time step. The
    agents are created when the simulation is started, and do not have to be
    made manually.

    .. py:attribute:: income

       The income of this agent

    .. py:attribute:: ambition

       How ambitious this agent is

    .. py:attribute:: certainty

       How certain this agents need to be before they are certain

    .. py:attribute:: need_money

       How much this agent needs money

    .. py:attribute:: need_green

       How much this agent wants green energy

    .. py:attribute:: need_safety

       How much this agent prefers safe forms of energy

    .. py:attribute:: need_government_money

       How much this agent prefers the government to have positive budget

    .. py:attribute:: energy_consumed

       How much energy this agent consumes per tick

    .. py:attribute:: refraction

       How long until this agent makes its next decision

    .. py:attribute:: friends

       All the friends that this agent has
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self,
                 simulation,
                 income,
                 ambition,
                 certainty,
                 need_money,
                 need_green,
                 need_safety,
                 need_government_money,
                 energy_consumed):
        # pylint: disable=too-many-arguments
        super(Agent, self).__init__(simulation)
        self.income = income
        self.ambition = ambition
        self.certainty = certainty
        self.need_money = need_money
        self.need_green = need_green
        self.need_safety = need_safety
        self.need_government_money = need_government_money
        self.energy_consumed = energy_consumed
        self.friends = AgentSet()
        self.refraction = randrange(self.simulation.refraction_ticks)
        self._satis = 0
        self._last_satis = self.simulation.current_tick
        self.company = None
        self.party = None

    @classmethod
    def generate_random(cls, simulation, avg_income, std_income, avg_energy_use, std_energy_use):
        """
        This generates a random agent from a set of settings and returns it.

        :param avg_income: The average income wanted for the population.
        :param std_income: The standard deviation for the income.
        """
        # pylint: disable=too-many-arguments
        income = -1
        while income < 1000:
            income = normalvariate(avg_income, std_income)
        energy_use = -1
        while energy_use < 500:
            energy_use = normalvariate(avg_energy_use, std_energy_use)
        return cls(simulation,
                   income=income,
                   energy_consumed=energy_use,
                   ambition=uniform(0, 100),
                   certainty=uniform(0, 100),
                   need_money=uniform(0, 100),
                   need_green=uniform(0, 100),
                   need_safety=uniform(0, 100),
                   need_government_money=uniform(0, 100))

    @property
    def uncertain(self):
        """
        If this agent is uncertain
        """
        same = self.friends.filter(lambda a: self.company == a.company)
        return (len(same)/len(self.friends) * 100) < self.certainty

    @property
    def unsatisfied(self):
        """
        If this agent is unsatisfied
        """
        return self.satisfaction < self.ambition

    @property
    def satisfaction(self):
        """
        How satisfied this agent is as a percentage
        """
        if self._last_satis == self.simulation.current_tick:
            return self._satis
        dist_money = self.company.product_cost
        if dist_money > self.need_money:
            dist_money *= 2
        dist_green = self.need_green - self.company.product_green
        if dist_green < 0:
            dist_green /= 2
        dist_safety = self.need_safety - self.company.product_safety
        if dist_safety < 0:
            dist_safety /= 2
        company_dist = dist_money + dist_green + dist_safety
        if company_dist < 0:
            company_dist = 0
        self._satis += (100 - company_dist - self._satis) / 20
        if self._satis < 1:
            self._satis = 1
        self._last_satis = self.simulation.current_tick
        return self._satis

    def make_friend(self, other):
        """
        Give this agent a new friend.
        """
        self.friends.add_agent(other)
        other.friends.add_agent(self)

    def tick(self):
        """
        Make a turn for this agent. In a turn, the agent will see if it has to make a decision
        about its energy provider and if so, pick a new one.
        """
        if not self.company:
            self.company = choice(self.simulation.companies)
        # If the agent needs to make a decision, make that decision
        self.refraction -= 1
        if self.refraction < 0:
            self.refraction = self.simulation.refraction_ticks
            if self.unsatisfied:
                if self.uncertain:
                    self.use_deliberation()
                else:
                    self.use_comparison()
            else:
                if self.uncertain:
                    self.use_imitation()
                else:
                    self.use_repetition()

    def choose_best_party(self):
        """
        Find the best party for this agent.
        """
        def party_satisfaction(party):
            "Calculate how satisfied this agent is with a party."
            return abs(mean(energy.greenness + energy.greenness * party.taxes[energy.name] / 100
                            for energy in self.simulation.energy_types) - self.need_green) + \
                   abs(mean(energy.safety + energy.safety * party.taxes[energy.name] / 100
                            for energy in self.simulation.energy_types) - self.need_safety) + \
                   abs(mean(energy.raw_price + energy.raw_price * party.taxes[energy.name] / 100
                            for energy in self.simulation.energy_types) - self.need_money) + \
                   random() * 5 - 10
                   #TODO: calculation if the party gets positive income
        self.party = min(self.simulation.parties, key=party_satisfaction)
        if party_satisfaction(self.party) < 0.20: # Non-voter
            self.party = None

    def use_deliberation(self):
        """
        If the agent is certain about itself, but unsatisfied, it will find the best company and
        join that.
        """
        self.company = min(self.simulation.companies, key=lambda c: dist(self, c))

    def use_comparison(self):
        """
        If the agent is unsatisfied and the agent is uncertain, then it will find the company that
        most of its friends are clients of.
        """
        friends_companies = set(friend.company for friend in self.friends)
        self.company = min(filter(lambda c: c in friends_companies, self.simulation.companies),
                           key=lambda c: dist(self, c))

    def use_imitation(self):
        """
        If the agent is satisfied, but uncertain, it will pick the most common company among its
        friends.
        """
        users = {}
        for company in self.simulation.companies:
            users[company] = 0
        for friend in self.friends:
            users[friend.company] += 1
        self.company = max(self.simulation.companies, key=lambda c: users[c])

    def use_repetition(self):
        """
        If the agent is satisfied and certain, it will just stay with its current provider.
        """
        pass

def dist(agent, company):
    "Calculate the distance between an agent and a company."
    return math.sqrt((agent.need_money - company.product_cost) ** 2 +
                     (agent.need_green - company.product_green) ** 2 +
                     (agent.need_safety - company.product_safety) ** 2)
