# BaseAgent.py

from abc import ABC, abstractmethod
from BaseAgent import Agent
class LearningAgent(Agent):
    @abstractmethod
    def act_and_train(self, state):
        """
           Given a state, selects and performs an action, and updates its policy (trains)
           Must return (observation, reward, done)
       """
        pass
