import os
from collections import deque

from SUMOextractor import extract
from agents.HeuristicAgent import HeuristicAgent
from agents.IndependentAgents import IndependentAgents
from agents.RandomAgent import RandomAgent
from graphics import save_results
from TrafficEnvironment import TrafficEnviron
def train(red, name, num_episodes=-1):

    model_path = os.path.join("models", name+".pth")
    plot_path = os.path.join("plots", name+".pth")

    # Get SUMO installation directory from environment variables to locate the executable
    sumo_home = os.getenv('SUMO_HOME')
    sumo_cmd = [os.path.join(sumo_home, "bin", "sumo"), "-c", os.path.join(sumo_home, f"{red}.sumocfg"), "--random"]

    # Get net information
    roads=extract(red,sumo_home)

    # Get SUMO installation directory from environment variables to locate the executable
    sumo_home = os.getenv('SUMO_HOME')
    sumo_cmd = [os.path.join(sumo_home, "bin", "sumo"), "-c", os.path.join(sumo_home, f"{red}.sumocfg"), "--random"]

    # Create environment linked to the simulation
    env = TrafficEnviron(sumo_cmd=sumo_cmd, roads=roads)

    # Create agents
    myagent=IndependentAgents(env, model_path=model_path)


    ep_rewards=[]
    ep_pollution=[]
    ep_waits=[]
    ep_bus_waits=[]
    cola_rewards=deque(maxlen=50)


    if(num_episodes==-1):

        early_stop=False
        patience = 40
        window = 30
        improvement_threshold=0.01
        worsening_threshold=0.2

        cumulative_sum=0
        cont=1
        best=-float('-inf')

        ep=1
        while(not early_stop):
            print(f"\n--- Episode {ep} ---")
            myagent.print_epsilon()
            observations = env.reset()[0]
            terminated = {agent: False for agent in env.agents}


            pollution = {"CO2": 0.0, "fuel": 0.0, "NOx": 0.0}
            wait = 0
            wait_bus = 0
            rewards = {agent: 0 for agent in env.agents}
            while not all(terminated.values()):

                observations, rewards_step, terminated, truncated = myagent.act_and_train(observations)
                for agent in env.agents:
                    rewards[agent] += rewards_step[agent]

                wait += env.get_total_waiting_time()
                wait_bus += env.get_total_bus_waiting_time()
                step_pollution = env.get_total_polution()
                for key in pollution:
                    pollution[key] += step_pollution[key]

            total_reward = sum(rewards.values())
            print(f"Total reward in episode {ep}: {total_reward}; Pollution: {pollution}")
            ep_rewards.append(total_reward)
            ep_pollution.append([pollution["CO2"], pollution["fuel"], pollution["NOx"]])
            ep_waits.append(wait)
            ep_bus_waits.append(wait_bus)
            if ep<=window:
                cola_rewards.append(total_reward)
                cumulative_sum+= total_reward
                if ep==window:
                    best=cumulative_sum/window
            else:
                cumulative_sum -= cola_rewards.popleft()
                cola_rewards.append(total_reward)
                cumulative_sum += total_reward
                mean=cumulative_sum/window
                print(f"Mean reward: {mean} --- Best: {best}")

                #condición de mejora
                if (mean - best) / abs(best) >= improvement_threshold:
                    best = mean
                    cont=0
                #condición de regresión
                elif (best - mean) / abs(best) >= worsening_threshold:
                    early_stop=True

                early_stop= early_stop or cont>=patience
            ep+=1
            cont+=1

    else:
        for ep in range(num_episodes):
            print(f"\n--- Episode {ep+1} ---")
            myagent.print_epsilon()
            observations = env.reset()[0]
            terminated = {agent: False for agent in env.agents}


            pollution = {"CO2": 0.0, "fuel": 0.0, "NOx": 0.0}
            wait=0
            wait_bus=0
            rewards = {agent: 0 for agent in env.agents}
            while  not all(terminated.values()):

                observations, rewards_step, terminated, truncated =myagent.act_and_train(observations)
                for agent in env.agents:
                    rewards[agent] += rewards_step[agent]


                wait+=env.get_total_waiting_time()
                wait_bus+=env.get_total_bus_waiting_time()
                step_pollution = env.get_total_polution()
                for key in pollution:
                    pollution[key] += step_pollution[key]

            total_reward = sum(rewards.values())
            print(f"Total reward in episode {ep+1}: {total_reward}; Pollution: {pollution}")
            ep_rewards.append(total_reward)
            ep_pollution.append([pollution["CO2"],pollution["fuel"],pollution["NOx"]])
            ep_waits.append(wait)
            ep_bus_waits.append(wait_bus)

    # Manually saving the model
    myagent.save_model()
    save_results(plot_path,name, ep_rewards,pollution=ep_pollution, waits=ep_waits,bus=ep_bus_waits)
    print("Rewards:")
    print(ep_rewards)
    print("Pollution")
    print(ep_pollution)
    env.close()

if __name__ == "__main__":
    #train(network_name, model_name,[num_episodes])
    name=f"eficiencbia"
    train("network",name)