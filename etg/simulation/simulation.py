"""
This module contains the simulation and all otherwise related functions.
"""
import datetime
from random import choice, randrange
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
    one_round = datetime.timedelta(days=730)

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
        self._old_government_budget = self.government_budget
        self.government_income = 0
        self._old_government_income = self.government_income
        self._old_greenness = 0
        self.votes = {}
        self.non_voters = 0
        self._setup_seasons(options['season_file'])
        self._generate_agents(options['agents'])
        self._setup_energy_types(options['energy_types'], options['agents']['avg_energy_use'])
        self._options = options

    def _setup_seasons(self, path):
        """
        Load the information for all the different seasons
        """
        self.seasons = []
        with open(path, 'r') as file:
            season_data = yaml.load_all(file)
            for data in season_data:
                self.seasons.append(Season(current_date=self.current_date, **data))
        season_candidate = None
        for season in self.seasons:
            start_date = season.start_date
            old_start = datetime.date(self.current_date.year, start_date.month, start_date.day)
            if old_start <= self.current_date:
                if not season_candidate or season_candidate.start_date < season.start_date:
                    season_candidate = season
        self.current_season = season_candidate

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

    def __setstate__(self, state):
        """
        Return the pickled simulation back to the original state.
        """
        self.__dict__.update(state)
        for agent in self.agents:
            agent.simulation = self
        for energy_type in self.energy_types:
            energy_type.simulation = self
        for party in self.parties:
            party.simulation = self
        for company in self.companies:
            company.simulation = self

    @property
    def days_until_election(self):
        """
        The number of days until the next election.
        """
        return (self.next_election - self.current_date).days

    @property
    def approval_rate(self):
        """
        The approval for the party that is currently in power. This is the percantage of voters that
        would vote for that party.
        """
        if self.active_party:
            return self.votes[self.active_party.name]/len(self.agents)
        else:
            return 0

    @property
    def greenness(self):
        """
        How green the energy consumed by the population is.
        """
        if len(self.companies) == 0:
            return 0
        else:
            return sum(etype.greenness *
                       sum(company.producers[etype.name].output + company.market[etype.name]
                           for company in self.companies) /
                       sum(company.output for company in self.companies)
                       for etype in self.energy_types)

    @property
    def change_government_income(self):
        "Difference in the income since the last election"
        return self.government_income - self._old_government_income

    @property
    def change_government_budget(self):
        "Difference in the government budget since the last election"
        return self.government_budget - self._old_government_budget

    @property
    def change_greenness(self):
        "Difference in the greenness of the energy consumed since the last election"
        return self.greenness - self._old_greenness

    def add_party(self, name, taxes, color):
        """
        Add a new political party to the simulation.
        """
        party = Party(self, self._options['party'], name)
        for tax in taxes:
            party.taxes[tax['name']] = tax['taxes']
        party.color = color
        self.parties.append(party)

    def add_company(self, name, unlocked_tiers, color):
        """
        Add a new company to the simulation.
        """
        company = Company(self, self._options['companies'], name)
        for tiers in unlocked_tiers:
            tier = tiers['tier']
            while tier > 0:
                tier -= 1
                company.producers[tiers['name']].upgrade()
        company.price = company.rawcost/company.output * 1.10
        company.color = color
        self.companies.append(company)

    def tick(self):
        """
        Iterate the simulation by one tick.
        """
        news = []
        for season in self.seasons:
            if season.should_trigger(self.current_date):
                season.trigger(self.current_date, self)
                news.append("It is now {season}!".format(season=season.name.capitalize()))
        for agent in self.agents:
            agent.tick()
        for company in self.companies:
            news.extend(company.tick())
        for party in self.parties:
            news.extend(party.tick())
        if self.current_date == self.next_election:
            self.next_election += self.one_round
            self.election()
            news.append("{} just got elected as the major party!".format(self.active_party.name))
        self.update_government_budget()
        if self.current_date.weekday() == 2: #weather only updates on wednesdays
            news.extend(self.update_weather())
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

    def update_weather(self):
        "Update the weather in the simulation."
        news = []
        weather = []
        for etype in self.energy_types:
            etype.failing = False
            prob = randrange(0, 100)
            if prob > etype.reliability[self.current_season.name]: # This type will fail
                tmp_weather = choice(etype.failure_weather)
                weather.append(tmp_weather)
                etype.failing = True
                news.append("The weather is {weather}! {type} power will not work tomorrow"\
                            .format(weather=tmp_weather, type=etype.name.capitalize()))
        if len(weather) == 0:
            self.weather = "sunny"
        elif len(weather) == 1:
            self.weather = weather[0]
        elif len(weather) == 2:
            self.weather = ' and '.join(weather)
        else:
            self.weather = ', '.join(weather[:-1]) + ', and ' + weather[-1]
        return news

    def poll(self):
        """
        Poll the population and return the results of the poll.
        """
        voters = {}
        non_voters = 0
        for party in self.parties:
            voters[party.name] = 0
        sample = self.agents.n_of(100)
        for agent in sample:
            agent.choose_best_party()
            if agent.party:
                voters[agent.party.name] += 1
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
            votes[party.name] = 0
        for agent in self.agents:
            agent.choose_best_party()
            if agent.party:
                votes[agent.party.name] += 1
            else:
                non_voters += 1
        self.active_party = max(self.parties, key=lambda p: votes[p.name])
        self.votes = votes
        self.non_voters = non_voters/len(self.agents) * 100
        self._old_government_income = self.government_income
        self._old_government_budget = self.government_budget
        self._old_greenness = self.greenness
        return (votes, non_voters)

class Season:
    """This class represents a single season for use within the game."""
    def __init__(self, name, start_date, current_date):
        start_date = datetime.datetime.strptime(start_date, "%B %d").date()
        self.name = name
        self.start_date = datetime.date(current_date.year, start_date.month, start_date.day)
        if current_date > self.start_date:
            self.start_date = datetime.date(current_date.year + 1, start_date.month, start_date.day)

    def __repr__(self):
        "Make a nice string format of the season"
        return "<Season {name} starts on {date}>".format(name=self.name, date=self.start_date)

    def should_trigger(self, current_date):
        "Returns if this next season should start"
        return self.start_date <= current_date

    def trigger(self, current_date, simulation):
        "Activate this new season if applicable."
        if not self.should_trigger(current_date):
            return False
        simulation.current_season = self
        year = self.start_date.year + 1
        month = self.start_date.month
        day = self.start_date.day
        self.start_date = datetime.date(year, month, day)
