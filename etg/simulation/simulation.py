"""
This module contains the simulation and all otherwise related functions.
"""
import datetime
from random import randrange
from etg.simulation.agent import Agent
from etg.util.agentset import AgentSet

class Simulation(object):
    """
    The actual simulation for the game.
    """
    # pylint: disable=too-many-instance-attributes
    one_day = datetime.timedelta(days=1)
    one_round = datetime.timedelta(days=1461)

    def __init__(self,
                 tick_rate,
                 refraction_ticks,
                 agent_options):
        """
        :param tick_rate: The number of seconds in a tick.
        :param refraction_ticks: The number of ticks between the decisions that an agent makes.
        :param agent_options: The options for the generation of the agents
        """
        self.agents = AgentSet()
        self.parties = []
        self.companies = []
        self.tick_rate = tick_rate
        self.refraction_ticks = refraction_ticks
        self._generate_agents(agent_options)
        self.current_tick = 1
        self.current_date = datetime.date.today()
        self.next_election = self.current_date + self.one_round

    def _generate_agents(self, agent_options):
        """
        :param number_agents: The number of agents in this simulation.
        :param seed_size: The size of the initial network of agents that is fully connected.
        :param max_friends: The maximum number of friends that an agent makes when initialized.
        :param chance_snd_friend: The chance that an agent does not make one, but two friends.
        """
        number_agents = agent_options['number_agents']
        seed_size = agent_options['seed_size']
        avg_income = agent_options['avg_income']
        std_income = agent_options['std_income']
        avg_energy_use = agent_options['avg_energy_use']
        std_energy_use = agent_options['std_energy_use']
        for _ in range(seed_size):
            self.agents.add_agent(Agent.generate_random(self, avg_income, std_income,
                                                        avg_energy_use, std_energy_use))
        for agent in self.agents:
            other = agent
            while other == agent:
                other = self.agents.one_of()
            agent.friends.add_agent(other)
            other.friends.add_agent(agent)
        def income_difference(agent, other):
            "Calculate the income difference between two agents, with randomness"
            return abs(other.income - agent.income + randrange(8000) - 4000)
        for _ in range(number_agents - seed_size):
            agent = Agent.generate_random(self, avg_income, std_income,
                                          avg_energy_use, std_energy_use)
            other = max(self.agents, key=lambda x: income_difference(agent, x))
            agent.friends.add_agent(other)
            other.friends.add_agent(agent)
            num_friends = min(agent_options['max_friends'], len(other.friends))
            for friend in other.friends.n_of(num_friends):
                agent.friends.add_agent(friend)
                friend.friends.add_agent(agent)

    @property
    def non_voters(self):
        """
        All the agents that are not planning to vote in the upcoming election.
        """
        return self.agents.filter(lambda a: a.party)

    def add_party(self, party):
        """
        Add a new political party to the simulation.
        """
        self.parties.append(party)

    def add_company(self, company):
        """
        Add a new company to the simulation.
        """
        self.companies.append(company)

    def tick(self):
        """
        Iterate the simulation by one tick.
        """
        for agent in self.agents:
            agent.tick()
        for company in self.companies:
            company.tick()
        for party in self.parties:
            party.tick()
        if self.current_date == self.next_election:
            pass
        self.current_tick += 1
        self.current_date += self.one_day
