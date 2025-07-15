import random
from agents.BaseAgent import Agent

class HeuristicAgent(Agent):
    """
        Agent that observes real-time traffic data and makes decisions based on a predefined heuristic rule
        Inherits from BaseAgent
    """

    def __init__(self, env):
        super().__init__(env)

    def act(self, state):
        actions={}
        for agent in self.env.agents:
            waiting=state[agent]["wait"]
            inline=state[agent]["lane_count"]
            sumi=waiting+30*inline
            actions[agent]=0
            if(sumi[0]+sumi[2]<sumi[1]+sumi[3]):
                actions[agent]=1
        observations, rewards_step, terminated, truncated, _ = self.env.step(actions)
        return observations, rewards_step, terminated, truncated


