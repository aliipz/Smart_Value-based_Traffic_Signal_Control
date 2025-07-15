# BaseAgent.py

from abc import ABC, abstractmethod

class Agent(ABC):
   def __init__(self, env):
    self.env = env

    @abstractmethod
    def act(self, state):
        """
            Given a state, selects and performs an action
            Must return (observation, reward, done)
        """
        pass

