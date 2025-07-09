# RandomAgent.py

import random
from agents.BaseAgent import Agent

class RandomAgent(Agent):
    """
        Agent that acts completely randomly
        Inherits from BaseAgent
    """

    def __init__(self, env):
        super().__init__(env)

    def act(self, state):
        actions = {agent: random.choice([0, 1]) for agent in self.env.agents}  # Acción aleatoria para cada agente

        # Tomar una acción en el entorno
        observations, rewards_step, terminated, truncated, _ = self.env.step(actions)
        return observations, rewards_step, terminated, truncated


