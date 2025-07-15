import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
from agents.BaseAgent import Agent
import os


class DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, output_dim)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)


class IndependentAgents(Agent):
    def __init__(self, env, model_path=None, update_target_every=50):
        super().__init__(env)

        # Parameters
        self.num_agents = len(env.agents)
        self.num_actions_per_agent = env.action_spaces[env.agents[0]].n
        self.agent_ids = env.agents

        #  Neural networks for each agent
        self.models = nn.ModuleDict({
            agent: DQN(12, self.num_actions_per_agent)  # (state dimension is 12)
            for agent in self.agent_ids
        })

        self.target_models = nn.ModuleDict({
            agent: DQN(12, self.num_actions_per_agent)
            for agent in self.agent_ids
        })

        for agent in self.agent_ids:
            self.target_models[agent].load_state_dict(self.models[agent].state_dict())
            self.target_models[agent].eval()

        #  Optimizers per agent
        self.optimizers = {
            agent: optim.Adam(self.models[agent].parameters(), lr=1e-3)
            for agent in self.agent_ids
        }

        #  Shared replay buffer
        self.memory = deque(maxlen=10000)

        # Hyperparameters
        self.batch_size = 64
        self.gamma =0.3
        self.epsilon = 1
        self.epsilon_decay = 0.9995
        self.epsilon_min = 0.05
        self.update_target_every = update_target_every
        self.train_step_counter = 0
        self.model_path = model_path
        self.criterion = nn.MSELoss()

        #Load models (if available)
        if model_path and os.path.exists(model_path):
            print(f"Loading models fromm: {model_path}")
            for agent in self.agent_ids:
                agent_path = os.path.join(model_path, f"{agent}.pt")
                if os.path.exists(agent_path):
                    self.models[agent].load_state_dict(torch.load(agent_path))
                    self.target_models[agent].load_state_dict(self.models[agent].state_dict())
            self.epsilon = self.epsilon_min

    def _get_agent_state(self, state_dict, agent):
        return np.concatenate([state_dict[agent]["wait"],
        state_dict[agent]["lane_count"],
        state_dict[agent]["bus_count"],
        ]).astype(np.float32)

    def act(self, state):
        actions = {}
        for agent in self.agent_ids:
            agent_state = self._get_agent_state(state, agent)
            state_tensor = torch.FloatTensor(agent_state).unsqueeze(0)

            with torch.no_grad():
                q_values = self.models[agent](state_tensor)
                actions[agent] = torch.argmax(q_values).item()

        next_state, rewards, terminated, truncated, _ = self.env.step(actions)
        return next_state, rewards, terminated, truncated

    def act_and_train(self, state):
        actions = {}
        if np.random.rand() < self.epsilon:
            actions = {agent: random.randint(0, self.num_actions_per_agent - 1) for agent in self.agent_ids}
        else:
            for agent in self.agent_ids:
                agent_state = self._get_agent_state(state, agent)
                state_tensor = torch.FloatTensor(agent_state).unsqueeze(0)

                with torch.no_grad():
                    q_values = self.models[agent](state_tensor)
                    actions[agent] = torch.argmax(q_values).item()

        next_state, rewards, terminated, truncated, _ = self.env.step(actions)

        self.remember(state, actions, rewards, next_state, terminated)
        self.train()

        return next_state, rewards, terminated, truncated

    def remember(self, state, actions, rewards, next_state, done):
        self.memory.append((state, actions, rewards, next_state, done))

    def train(self):
        if len(self.memory) < self.batch_size:
            return

        batch = random.sample(self.memory, self.batch_size)

        for agent in self.agent_ids:
            states = []
            agent_actions = []
            rewards = []
            next_states = []
            dones = []

            # ==== Given a past experience, executes DQN algorithm ===

            # Collect agent-specific data from the batch
            for transition in batch:
                state, actions, reward_dict, next_state, done_dict = transition
                states.append(self._get_agent_state(state, agent))
                agent_actions.append(actions[agent])
                rewards.append(reward_dict[agent])
                next_states.append(self._get_agent_state(next_state, agent))
                dones.append(done_dict[agent])

            # Convert to tensors
            states_tensor = torch.FloatTensor(np.array(states))
            actions_tensor = torch.LongTensor(agent_actions)
            rewards_tensor = torch.FloatTensor(rewards)
            next_states_tensor = torch.FloatTensor(np.array(next_states))
            dones_tensor = torch.BoolTensor(dones)

            # Calculate current Q-values
            current_q = self.models[agent](states_tensor).gather(1, actions_tensor.unsqueeze(1)).squeeze(1)

            # Calculate y^t target value
            with torch.no_grad():
                next_q = self.target_models[agent](next_states_tensor).max(1)[0]
                target_q = rewards_tensor + self.gamma * next_q * (~dones_tensor)

            # Training step: compute loss and update model
            loss = self.criterion(current_q, target_q)
            self.optimizers[agent].zero_grad()
            loss.backward()
            self.optimizers[agent].step()

        # Update target networks and save model periodically
        self.train_step_counter += 1
        if self.train_step_counter % self.update_target_every == 0:
            for agent in self.agent_ids:
                self.target_models[agent].load_state_dict(self.models[agent].state_dict())

            if self.model_path:
                self.save_model()

        # Epsilon decay
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save_model(self):
        if self.model_path:
            os.makedirs(self.model_path, exist_ok=True)
            for agent in self.agent_ids:
                agent_path = os.path.join(self.model_path, f"{agent}.pt")
                torch.save(self.models[agent].state_dict(), agent_path)
            print(f"Models saved in: {self.model_path}")

    def load_model(self):
        if self.model_path and os.path.exists(self.model_path):
            for agent in self.agent_ids:
                agent_path = os.path.join(self.model_path, f"{agent}.pt")
                if os.path.exists(agent_path):
                    self.models[agent].load_state_dict(torch.load(agent_path))
                    self.target_models[agent].load_state_dict(self.models[agent].state_dict())
            print(f"Models loaded from: {self.model_path}")

    def print_epsilon(self):
        print(f"epsilon={self.epsilon}")