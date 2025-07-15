import traci
import numpy as np
from gymnasium import spaces
import gymnasium as gym
from pandas.io.formats.format import format_array


class TrafficEnviron(gym.Env):
    def __init__(self, sumo_cmd=None, roads=None):
        super().__init__()
        if roads is None:
            roads = {}
        self.sumo_cmd = sumo_cmd
        self.changeTime = 30
        self.new = True
        self.MAX_WAIT_TIME = 500
        self.intersections = list(roads.keys())
        self.roads = roads
        self.vehicle_routes = {}
        self.possible_agents = self.intersections
        self.agents = self.possible_agents[:]
        self.action_spaces = {
            agent: spaces.Discrete(2) for agent in self.agents
        }

        self.possible_actions = ["GGgrrrGGgrrr", "rrrGGgrrrGGg"]
        self.observation_spaces = {
            agent: spaces.Dict({
                "wait": spaces.Box(low=0, high=np.inf, shape=(4,), dtype=np.float32),
                "lane_count": spaces.Box(low=0, high=np.inf, shape=(4,), dtype=np.float32),
                "bus_count": spaces.Box(low=0, high=np.inf, shape=(4,), dtype=np.float32),
            }) for agent in self.agents
        }

        self.pollution_ac = {
            agent: {"CO2": 0.0, "fuel": 0.0, "NOx": 0.0}
            for agent in self.agents
        }
        self.prev_stopped = {agent: set() for agent in self.agents}
        self.new_stops={agent: 0 for agent in self.agents}


        print(self.sumo_cmd)
        traci.start(self.sumo_cmd)

    def reset(self, seed=None, options=None):
        if not self.new:
            k = 9
            traci.close()
            traci.start(self.sumo_cmd)
        self.new = False
        self.agents = self.possible_agents[:]
        return {agent: self._get_observation(agent) for agent in self.agents}, {}

    def step(self, actions):
        if(actions!= None):
            for agent, action in actions.items():
                self._changeLight(agent, action)

        # Clears accumulated pollution per intersection
        self.pollution_ac = {
            agent: {"CO2": 0.0, "fuel": 0.0, "NOx": 0.0}
            for agent in self.agents
        }
       # self.new_stops = {agent: 0 for agent in self.agents}

        # Updates metrics
        for _ in range(self.changeTime):
            self._update_routes()
            self._update_pollution()
           # self._update_stopped()
            traci.simulationStep()

        # Returns observations, rewards, terminated, truncated
        observations = {agent: self._get_observation(agent) for agent in self.agents}
        rewards = {agent: self._get_reward(agent) for agent in self.agents}
        terminated = {agent: traci.simulation.getCurrentTime() >= 3600000 for agent in self.agents}
        truncated = {agent: False for agent in self.agents}
        return observations, rewards, terminated, truncated, {}

    def get_routes(self):
        return self.vehicle_routes

    def _update_routes(self):
        current_time = traci.simulation.getTime()

        # Log vehicle entry to the network
        for veh_id in traci.simulation.getDepartedIDList():
            route = traci.vehicle.getRoute(veh_id)
            origin = route[0] if route else None
            destination = route[-1] if route else None
            self.vehicle_routes[veh_id] = {
                "origin": origin,
                "destination": destination,
                "start_time": current_time,
                "end_time": None,
                "complete_route": route,
                "type":traci.vehicle.getTypeID(veh_id)
            }

        # Log vehicle exit from the network
        for veh_id in traci.simulation.getArrivedIDList():
            if veh_id in self.vehicle_routes:
                self.vehicle_routes[veh_id]["end_time"] = current_time

    def _changeLight(self, nagent, naction):
        traci.trafficlight.setRedYellowGreenState(nagent, self.possible_actions[naction])

    def _get_observation(self, agent):
        lane_ids = [f"{self.roads[agent][i]}_0" for i in range(4)]

        waiting = np.array([traci.lane.getWaitingTime(lane) for lane in lane_ids], dtype=np.float32)
        inline = np.array([traci.lane.getLastStepVehicleNumber(lane) for lane in lane_ids], dtype=np.float32)

        def bus_counter(lane_id):
            vehicles = traci.lane.getLastStepVehicleIDs(lane_id)
            return sum(1 for v in vehicles if traci.vehicle.getTypeID(v).lower() == "bus")

        buses = np.array([bus_counter(lane) for lane in lane_ids], dtype=np.float32)

        return {
            "wait": waiting,
            "lane_count": inline,
            "bus_count": buses
        }

    # Design your own Reward Function
    def _get_reward(self, agent):
        waiting = self._get_wait(agent)
        pollution = self._get_pollution(agent)
        bus_waiting=self._get_wait_buses(agent)
        return -waiting   #-pollution["CO2"]/10  -pollution["fuel"]/10-10*bus_waiting -pollution["NOx"]/10 -15*self.new_stops[agent]

    # Local waiting time and pollution

    def _get_wait(self, agent):
        lanes = [f"{self.roads[agent][i]}_0" for i in range(4)]
        waiting = sum([traci.lane.getWaitingTime(l) for l in lanes])
        return waiting

    def _get_wait_buses(self, agent):
        lanes = [f"{self.roads[agent][i]}_0" for i in range(4)]
        bus_waiting = 0
        for lane in lanes:
            vehs = traci.lane.getLastStepVehicleIDs(lane)
            for veh in vehs:
                if traci.vehicle.getTypeID(veh).lower() == "bus":
                    speed = traci.vehicle.getSpeed(veh)
                    if speed < 0.1:  # We consider the bus to be waiting
                        bus_waiting += traci.vehicle.getWaitingTime(veh)
        return bus_waiting

    # Returns the pollution emitted from the last state to the current state
    def _get_pollution(self, agent):
        lanes = [f"{self.roads[agent][i]}_0" for i in range(4)]
        # nox = sum([traci.lane.getNOxEmission(l) for l in lanes])
        # co2 = sum([traci.lane.getCO2Emission(l) for l in lanes]) # getFuelConsumption traci.lane.getCO2Emission(f"{self.roads[agent][3]}_0") +
        return self.pollution_ac[agent]

    # Updates pollution metrics
    def _update_pollution(self):
        for agent in self.agents:
            lanes = [f"{self.roads[agent][i]}_0" for i in range(4)]

            co2 = sum([traci.lane.getCO2Emission(l) for l in lanes])
            fuel = sum([traci.lane.getFuelConsumption(l) for l in lanes])
            nox = sum([traci.lane.getNOxEmission(l) for l in lanes])

            self.pollution_ac[agent]["CO2"] += co2
            self.pollution_ac[agent]["fuel"] += fuel
            self.pollution_ac[agent]["NOx"] += nox

    def _get_stopped(self):
        for agent in self.agents:
            stopped = set()
            lanes = [f"{self.roads[agent][i]}_0" for i in range(4)]

            for lane in lanes:
                veh_ids = traci.lane.getLastStepVehicleIDs(lane)
                for veh_id in veh_ids:
                    if traci.vehicle.getSpeed(veh_id) < 0.1:
                        stopped.add(veh_id)
            self.prev_stopped[agent] = stopped
    def _update_stopped(self):
        for agent in self.agents:

            lanes = [f"{self.roads[agent][i]}_0" for i in range(4)]
            new_stops=0
            for lane in lanes:
                veh_ids = traci.lane.getLastStepVehicleIDs(lane)
                for veh_id in veh_ids:
                    if traci.vehicle.getSpeed(veh_id) < 0.1:
                        if not veh_id in self.prev_stopped[agent]:
                            self.prev_stopped[agent].add(veh_id)
                            new_stops += 1
            self.new_stops[agent] += new_stops

    # Total waiting time, pollution, and bus waiting time

    def get_total_waiting_time(self):
        wait = 0
        for agent in self.agents:
            wait += self._get_wait(agent)
        return wait

    def get_total_polution(self):
        total = {"CO2": 0.0, "fuel": 0.0, "NOx": 0.0}
        for agent in self.agents:
            p = self._get_pollution(agent)
            for key in total:
                total[key] += p[key]
        return total

    def get_total_bus_waiting_time(self):
        wait = 0
        for agent in self.agents:
            wait += self._get_wait_buses(agent)
        return wait

    def _check_time_limit(self):
        for agent in self.agents:
            espera_1 = traci.lane.getWaitingTime(f"{self.roads[agent][0]}_0")
            espera_2 = traci.lane.getWaitingTime(f"{self.roads[agent][1]}_0")
            espera_3 = traci.lane.getWaitingTime(f"{self.roads[agent][2]}_0")
            espera_4 = traci.lane.getWaitingTime(f"{self.roads[agent][3]}_0")

            total_wait_time = espera_1 + espera_2 + espera_3 + espera_4
            if total_wait_time > self.MAX_WAIT_TIME:
                return True  # Ends the episode if the total waiting time exceeds the threshold for any agent

        return False

    def close(self):
        traci.close()
