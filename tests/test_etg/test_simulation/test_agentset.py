"""
A testing suite for the `etg.simulation.agentset` module
"""
from twisted.trial import unittest
from etg.util.agentset import AgentSet

class AgentSetTestCase(unittest.TestCase):
    """
    Testing the behaviours for the agent set.
    """

    def test_len(self):
        """
        A test to make sure that `len` works properly.
        """
        self.assertEqual(len(AgentSet(1, 2, 3, 4, 5)), 5)
        self.assertEqual(len(AgentSet([1, 2, 3, 4, 5])), 1)
        self.assertEqual(len(AgentSet(_list=[1, 2, 3, 4, 5])), 5)
        self.assertEqual(len(AgentSet(_iter=set([1, 2, 3, 4, 5]))), 5)

    def test_contains(self):
        """
        A test to make sure that `in` works properly.
        """
        agents = AgentSet(1, 2, 3, 4, 5)
        self.assertTrue(3 in agents)
        self.assertFalse(7 in agents)
        self.assertFalse(3 not in agents)
        self.assertTrue(7 not in agents)

    def test_add(self):
        """
        A test to make sure that agents get added to the set.
        """
        agents = AgentSet(_iter=range(10))
        agents.add_agent(20)
        self.assertTrue(20 in agents)

    def test_remove(self):
        """
        A test to make sure that agents get properly removed.
        """
        agents = AgentSet(_iter=range(10))
        agents.remove_agent(5)
        self.assertTrue(5 not in agents)

    def test_iter(self):
        """
        A test to make sure that the agents get properly shuffled. Uses
        randomness, so might occasionally fail.
        """
        agents = AgentSet(_iter=range(100))
        sets = []
        for _ in range(5):
            permutation = list(agents)
            self.assertTrue(permutation not in sets,
                            "There are two agent sets with the same order! Rerun to make sure")
            sets.append(permutation)
