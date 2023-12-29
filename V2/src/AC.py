#!/usr/bin/env python

import numpy as np

import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from src import Car
import pygame as PG
import sys 
import math

from collections import deque

class GenericNetwork(nn.Module):
    def __init__(self, lr, state_size, action_size, layer1_dims, layer2_dims):
        super(GenericNetwork, self).__init__()

        self.lr = lr
        self.state_size = state_size
        self.action_size = action_size 

        self.fc1 = nn.Linear(self.state_size, layer1_dims)
        self.fc2 = nn.Linear(layer1_dims, layer2_dims)
        self.fc3 = nn.Linear(layer2_dims, self.action_size)

        self.optimizer = optim.Adam(self.parameters(), lr=self.lr)
        self.device = T.device('cuda:0' if T.cuda.is_available() else 'cpu')
        self.to(self.device)

    def forward(self, observation):
        state = T.tensor(observation, dtype=T.float).to(self.device)
        y1 = F.relu(self.fc1(state))
        y2 = F.relu(self.fc2(y1))
        y3 = self.fc3(y2)

        return y3

class GenericNetwork2(nn.Module):
    def __init__(self, lr, state_size, action_size, layer1_dims):
        super(GenericNetwork2, self).__init__()

        self.lr = lr
        self.state_size = state_size
        self.action_size = action_size 

        self.fc1 = nn.Linear(self.state_size, layer1_dims)
        self.fc2 = nn.Linear(layer1_dims, self.action_size)

        self.optimizer = optim.Adam(self.parameters(), lr=self.lr)
        self.device = T.device('cuda:0' if T.cuda.is_available() else 'cpu')
        self.to(self.device)

    def forward(self, observation):
        state = T.tensor(observation, dtype=T.float).to(self.device)
        y1 = F.relu(self.fc1(state))
        y2 = self.fc2(y1)

        return y2


class ActorCritic:
    def __init__(self, alpha, beta, gamma=0.99, action_size=2, state_size=6,
                 layer1_dims=64, layer2_dims=64):

        self.action_size = action_size 
        self.state_size = state_size 
        
        self.gamma = gamma

        self.log_probs = None
        
        self.actor  = GenericNetwork(alpha, state_size, 2*self.action_size, layer1_dims, layer2_dims)
        self.critic = GenericNetwork(beta, state_size, 1, layer1_dims, layer2_dims)

        self.softplus = T.nn.Softplus()
                 
    def action(self, observation):
        mu, sigma = self.actor.forward(observation)
        sigma = self.softplus(sigma) + 0.0001
        distr = T.distributions.Normal(mu, sigma)

        probs = distr.sample(sample_shape=T.Size([1]))
        self.log_probs = distr.log_prob(probs).to(self.actor.device)
                    
        action = T.tanh(probs).item()

        return action

    def learn(self, observation, reward, next_observation, done):
        self.actor.zero_grad()
        self.critic.zero_grad()

        critic_value = self.critic.forward(observation)
        critic_value_next = self.critic.forward(next_observation)

        reward = T.tensor(reward, dtype=T.float).to(self.actor.device)

        target = reward + self.gamma*critic_value_next*(1-int(done))
        delta = target - critic_value # advantage

        assert self.log_probs is not None

        actor_loss = -self.log_probs * delta
        critic_loss = delta**2

        (actor_loss + critic_loss).mean().backward()

        self.actor.optimizer.step()
        self.critic.optimizer.step()

def Run(screen : PG.Surface, clock : PG.time.Clock, cars : Car.Cars, map : np.ndarray, max_runs=-1):
    surface = PG.surfarray.make_surface(map)

    ALPHA = 0.0001
    BETA = 0.0001
    arch = [(256,256), (256,128), (128,128)]

    assert len(arch) == cars.count, f"{len(arch)} not equal to {cars.count} car count"

    ac_pairs = []
    for l1,l2 in arch:
        power = ActorCritic(ALPHA, BETA, 0.999, action_size=1, state_size=6,
                                layer1_dims=l1, layer2_dims=l2)

        steer = ActorCritic(ALPHA, BETA, 0.999, action_size=1, state_size=6,
                                layer1_dims=l1, layer2_dims=l2)
        # power = ActorCritic(ALPHA, BETA, 0.999, action_size=1, state_size=6,
        #                         layer1_dims=l1)

        # steer = ActorCritic(ALPHA, BETA, 0.999, action_size=1, state_size=6,
        #                         layer1_dims=l1)

        ac_pairs.append((power,steer))

    runs = 0
    while runs < max_runs or max_runs == -1:
        cars.reset()

        obs = np.zeros([cars.count,6])

        last_reward = np.zeros([cars.count])
        cum_rewards = np.zeros([cars.count])

        last_alive = np.ones([cars.count])
        while cars.any_alive():
            screen.blit(surface, (0,0))
            cars.draw(screen)

            for event in PG.event.get():
                if event.type == PG.QUIT:
                    sys.exit(0)

            inputs = np.zeros([cars.count, 2])
            for i, (p, s) in enumerate(ac_pairs):
                if not cars.alive_list[i]: continue
                a = p.action(obs[i])
                b = s.action(obs[i])

                inputs[i][0] = a
                inputs[i][1] = b

            cars.input_controller(inputs)
            cars.update()
            next_obs = cars.observation(screen, False)

            # reward calc needs to improve
            new_reward = cars.calc_fitness_immediate()

            reward = new_reward - last_reward
            # print(reward)

            cum_rewards += reward
            for i, (p, s) in enumerate(ac_pairs):
                if not last_alive[i]: continue

                p.learn(obs[i], reward[i], next_obs[i], not cars.alive_list[i])
                s.learn(obs[i], reward[i], next_obs[i], not cars.alive_list[i])

                if not cars.alive_list[i]:
                    last_alive[i] = 0

            PG.display.flip()
            # clock.tick(60)

            obs = next_obs
            last_reward = new_reward

        print(runs, cum_rewards)
        runs += 1

