import os

from typing import Literal
import pandas as pd

from numpy import var, mean

from SUMOextractor import extract
from agents.FixedAgent import FixedAgent
from agents.HeuristicAgent import HeuristicAgent
from agents.IndependentAgents import IndependentAgents
from agents.RandomAgent import RandomAgent
from TrafficEnvironment import TrafficEnviron
from graphics import save_results
def test(red, mode: Literal["heuristic", "independent", "random", "fixed"], path=""):
    if( mode!="independent" and mode!="heuristic" and mode!="random" and mode!="fixed"):
        return

    model_path = os.path.join("models", path)

    # Get SUMO installation directory from environment variables to locate the executable
    sumo_home = os.getenv('SUMO_HOME')
    print(sumo_home)
    sumo_cmd = [os.path.join(sumo_home, "bin", "sumo"), "-c", os.path.join(sumo_home, f"{red}.sumocfg"), "--random"]

    # Get net information
    roads=extract(red,sumo_home)



    # Create environment linked to the simulation
    env = TrafficEnviron(sumo_cmd=sumo_cmd, roads=roads)

    # Create agents


    if(mode=="independent"):
        myagent=IndependentAgents(env, model_path=model_path)
    elif(mode=="heuristic"):
        myagent=HeuristicAgent(env)
    elif(mode=="fixed"):
        myagent=FixedAgent(env)
    else:
        myagent=RandomAgent(env)




    observations = env.reset()[0]
    terminated = {agent: False for agent in env.agents}
    rewards = {agent: 0 for agent in env.agents}
    wait=0
    pollution = {"CO2": 0.0, "fuel": 0.0, "NOx": 0.0}

    while  not all(terminated.values()):

        observations, rewards_step, terminated, truncated =myagent.act(observations)
        for agent in env.agents:
            rewards[agent] += rewards_step[agent]
        wait+=env.get_total_waiting_time()
        step_pollution=env.get_total_polution()
        for key in pollution:
            pollution[key] += step_pollution[key]

    total_reward = sum(rewards.values())
    print(f"Total reward: {total_reward}")
    print(f"Total waiting time: {wait}")
    print(f"Total pollution: {pollution}")

    env.close()
    routes=env.get_routes()
    wait,m,v,bus_wait,m_bus, v_bus=evaluate(routes)
    return wait, m, v, bus_wait, m_bus, v_bus, pollution

def evaluate(routes):
    travel_time=[]
    expected_durations=[]
    delay=[]
    delay_per=[]

    bus_travel_time=[]
    bus_expected_durations=[]
    bus_delay=[]
    bus_delay_per=[]

    for veh_id, info in routes.items():
        start = info.get("start_time")
        end = info.get("end_time")
        expected_duration=len(info.get("complete_route"))*8
        vtype=info.get("type")

        if start is not None and end is not None:
            duration = end - start
            if(vtype=="bus"):
                bus_travel_time.append(duration)
                bus_delay.append(duration-expected_duration)
                bus_expected_durations.append(expected_duration)
                bus_delay_per.append((duration-expected_duration)*100/expected_duration)
            else:
                travel_time.append(duration)
                delay.append(duration - expected_duration)
                expected_durations.append(expected_duration)
                delay_per.append((duration - expected_duration) * 100 / expected_duration)

        else: #Manage non-terminated trips
            #travel_time.append(float('-inf'))
            #delay.append(float('-inf'))
            #expected_durations.append(expected_duration)
            a=2

    print(f"Total delay = {sum(delay)}, mean and variance of delay: {mean(delay)}, {var(delay)}. The average trip duration increased by {mean(delay_per):.1f}%")
    print(f"Total public transport delay = {sum(bus_delay)}, mean and variance of public transport delay: {mean(bus_delay)}, {var(bus_delay)}. The average trip duration increased by {mean(bus_delay_per):.1f}%")
    return sum(delay),mean(delay), var(delay), sum(bus_delay), mean(bus_delay), var(bus_delay)


def big_test(red, mode: Literal["heuristic", "independent", "random", "fixed"], path="", n=10):

    wait=0
    meanw=0
    varw=0
    bus_wait=0
    meanbw=0
    varbw=0
    pollution= {"CO2": 0.0, "fuel": 0.0, "NOx": 0.0}
    for i in range(1,n+1):
        e,m,v,eb,mb,vb,c=test(red,mode, path)
        wait+=e
        meanw+=m
        varw+=v
        bus_wait+=eb
        meanbw+=mb
        varbw+=vb
        pollution["CO2"]+=c["CO2"]
        pollution["fuel"]+=c["fuel"]
        pollution["NOx"]+=c["NOx"]
    wait/=n
    meanw/=n
    varw/=n
    pollution["CO2"]/=n
    pollution["fuel"]/=n
    pollution["NOx"]/=n
    bus_wait/=n
    meanbw/=n
    varbw/=n
    print()
    print()
    print("RESULTS")
    print(f"Total delay: {wait}; Mean delay: {meanw}; Variance: {varw}")
    print(f"Total public transport delay: {bus_wait}; Mean delay: {meanbw}; Variance: {varbw}")
    print(f"Pollution: {pollution}")

    return [wait,meanw,varw,bus_wait,meanbw,varbw, pollution["CO2"], pollution["fuel"], pollution["NOx"]]


if __name__ == "__main__":
    name = f"efficiency.pth"

    # big_test(network_name,agent_mode, [model_path],episodes)
    big_test("network", "independent",name, n=10)



