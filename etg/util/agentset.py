"""
A class to mimic Netlogos agentsets iteration behaviour
"""
import random

class AgentSet:
    """
    A class to mimic Netlogo's agentsets random iteration behaviour. Also has
    some convience methods that making common sequence operations for which
    order does not matter faster.
    """
    def __init__(self, *args, _list=None, _iter=None):
        """
        An object can be initialized by giving the agents that shoudl initially
        be in the set in its constructor.
        """
        if _list:
            self._list = _list
        elif _iter:
            self._list = list(_iter)
        else:
            self._list = list(args)

    def __iter__(self):
        """
        Return an iterator that goes over the agents in a random order.
        """
        return iter(random.sample(self._list, len(self._list)))

    def __len__(self):
        """
        Get the number of agents in this agentset.
        """
        return len(self._list)

    def __contains__(self, agent):
        """
        A check to see if a certain agent is in the set.
        """
        return agent in self._list

    def add_agent(self, agent):
        """
        Add an agent to the agent set. If the agent is already in the set, do
        nothing.
        """
        if agent not in self._list:
            self._list.append(agent)

    def remove_agent(self, agent):
        """
        Remove an agent from the set. If the agent is not in the set, do
        nothing.
        """
        self._list.remove(agent)

    def n_of(self, number):
        """
        Return number of agents from the set, as an :class:`~etg.util.agentset.AgentSet`.
        """
        ret = AgentSet()
        for agent in self:
            ret.add_agent(agent)
            if len(ret) >= number:
                break
        return ret

    def one_of(self):
        """
        Return a random agent from the set.
        """
        # pylint: disable=protected-access
        for agent in self.n_of(1):
            return agent

    def filter(self, predicate):
        """
        A more efficient filter that works directly on the underlaying
        datastructure, and therefore does not shuffle the list first. If order
        is not important for the filtering, this method is preferred over the
        built in filter
        """
        return AgentSet(_iter=filter(predicate, self._list))
