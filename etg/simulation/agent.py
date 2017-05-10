"""
All classes and methods having to do with agents
"""
from random import choice, randrange, normalvariate, uniform
import math
from ..util.agentset import AgentSet
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
        pass

    @property
    def unsatisfied(self):
        """
        If this agent is unsatisfied
        """
        pass

    @property
    def satisfaction(self):
        """
        How satisfied this agent is as a percentage
        """
        pass
