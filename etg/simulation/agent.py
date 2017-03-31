"""
All classes and methods having to do with agents
"""
from random import randrange
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
        super(Agent, self).__init__(self, simulation)
        self.income = income
        self.ambition = ambition
        self.certainty = certainty
        self.need_money = need_money
        self.need_green = need_green
        self.need_safety = need_safety
        self.need_government_money = need_government_money
        self.energy_consumed = energy_consumed
        self.friends = AgentSet()
        self.refraction = randrange(self.simulation.agent_refraction)
        self.company = None
        self.party = None

    @property
    def is_uncertain(self):
        """
        If this agent is uncertain
        """
        pass

    @property
    def is_unsatisfied(self):
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
