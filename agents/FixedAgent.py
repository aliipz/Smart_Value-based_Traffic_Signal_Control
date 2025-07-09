import random
from agents.BaseAgent import Agent

class FixedAgent(Agent):
    """
        Agent with fixed-time cycles, no adapting to real-traffic conditions
        Inherits from BaseAgent
    """

    def __init__(self, env):
        super().__init__(env)
        self.next_phase={}
        for agent in self.env.agents:
            self.next_phase[agent]=(random.randint(0, 1))


    def act(self, state):
        actions={}
        for agent in self.env.agents:
            if(self.next_phase[agent]==0):
                actions[agent] = 0
            else:
                actions[agent] = 1
            self.next_phase[agent] = self.next_phase[agent] ^ 1
        observations, rewards_step, terminated, truncated, _ = self.env.step(actions)
        return observations, rewards_step, terminated, truncated


