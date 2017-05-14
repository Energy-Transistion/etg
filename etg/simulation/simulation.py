"""
This module contains the simulation and all otherwise related functions.
"""
import datetime
from random import randrange
import yaml
from etg.simulation.agent import Agent
from etg.simulation.company import Company
from etg.simulation.party import Party
from etg.simulation.energy import EnergyType
from etg.util.agentset import AgentSet

class Simulation(object):
    """
    The actual simulation for the game.
    """
    # pylint: disable=too-many-instance-attributes
    one_day = datetime.timedelta(days=1)
    one_round = datetime.timedelta(days=1461)

    def __init__(self,
                 options):
        """
        :param tick_rate: The number of seconds in a tick.
        :param refraction_ticks: The number of ticks between the decisions that an agent makes.
        :param agent_options: The options for the generation of the agents
        """
        self.agents = AgentSet()
        self.parties = []
        self.companies = []
        self.tick_rate = options['tick_rate']
        self.refraction_ticks = options['refraction_ticks']
        self.current_tick = 1
        self.current_date = datetime.date.today()
        self.weather = "sunny"
        self.next_election = self.current_date + self.one_round
        self.active_party = None
        self.government_budget = options['government_budget']
        self.government_income = 0
        self.votes = {}
        self.non_voters = 0
        self._generate_agents(options['agents'])
        self._setup_energy_types(options['energy_types'], options['agents']['avg_energy_use'])
        self._options = options

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
            agent.make_friend(other)
        def income_difference(agent, other):
            "Calculate the income difference between two agents, with randomness"
            return abs(other.income - agent.income + randrange(8000) - 4000)
        for _ in range(number_agents - seed_size):
            agent = Agent.generate_random(self, avg_income, std_income,
                                          avg_energy_use, std_energy_use)
            other = max(self.agents, key=lambda x: income_difference(agent, x))
            agent.make_friend(other)
            num_friends = min(agent_options['max_friends'], len(other.friends))
            for friend in other.friends.n_of(num_friends):
                agent.make_friend(friend)
            self.agents.add_agent(agent)

    def _setup_energy_types(self, path, avg_energy_use):
        """
        This method sets up all the necessary information for the different energy types.
        """
        self.energy_types = []
        with open(path, 'r') as file:
            energy_types_data = yaml.load_all(file)
            for data in energy_types_data:
                initial_energy = data['initial_output'] /100 * len(self.agents) * avg_energy_use
                del data['initial_output']
                self.energy_types.append(EnergyType(simulation=self,
                                                    initial_output=initial_energy, **data))

    @property
    def approval(self):
        """
        The approval for the party that is currently in power. This is the percantage of voters that
        would vote for that party.
        """
        return self.votes[self.active_party]/len(self.agents)

    def add_party(self, name, taxes):
        """
        Add a new political party to the simulation.
        """
        party = Party(self, self._options['party'], name)
        for tax in taxes:
            party.taxes[tax['name']] = tax['taxes']
        self.parties.append(party)

    def add_company(self, name, unlocked_tiers):
        """
        Add a new company to the simulation.
        """
        company = Company(self, self._options['companies'], name)
        for tiers in unlocked_tiers:
            tier = tiers['tier']
            while tier > 0:
                tier -= 1
                company.producers[tiers['name']].upgrade()
        self.companies.append(company)

    def tick(self):
        """
        Iterate the simulation by one tick.
        """
        news = []
        for agent in self.agents:
            agent.tick()
        for company in self.companies:
            company.tick()
        for party in self.parties:
            party.tick()
        if self.current_date == self.next_election:
            self.next_election += self.one_round
            self.election()
            news.append("{} just got elected as the major party!".format(self.active_party.name))
        self.update_government_budget()
        self.current_tick += 1
        self.current_date += self.one_day
        return news

    def update_government_budget(self):
        """
        Update the government budget by inning taxes.
        """
        self.government_income = sum(agent.energy_consumed * agent.company.taxes
                                     for agent in self.agents)
        self.government_budget += self.government_income

    def poll(self):
        """
        Poll the population and return the results of the poll.
        """
        voters = {}
        non_voters = 0
        for party in self.parties:
            voters[party] = 0
        sample = self.agents.n_of(100)
        for agent in sample:
            agent.choose_best_party()
            if agent.party:
                voters[agent.party] += 1
            else:
                non_voters += 1
        self.votes = voters
        self.non_voters = non_voters
        return (voters, non_voters)

    def election(self):
        """
        Hold an election and put the party with most voters in power.
        """
        votes = {}
        non_voters = 0
        for party in self.parties:
            votes[party] = 0
        for agent in self.agents:
            agent.choose_best_party()
            if agent.party:
                votes[agent.party] += 1
            else:
                non_voters += 1
        self.active_party = max(self.parties, key=lambda p: votes[p])
        self.votes = votes
        self.non_voters = non_voters
        return (votes, non_voters)
