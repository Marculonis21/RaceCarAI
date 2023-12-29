#!/usr/bin/env python

import numpy as np

import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from src import Car
import pygame as PG
import sys 


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

        

class ActorCritic:
    def __init__(self, alpha, beta, gamma=0.99, action_size=2, state_size=6,
                 layer1_dims=64, layer_2_dims=32):

        self.action_size = action_size 
        self.state_size = state_size 
        
        self.gamma = gamma

        self.log_probs = None
        
        self.actor  = GenericNetwork(alpha, state_size, 2*self.action_size, layer1_dims, layer_2_dims )
        self.critic = GenericNetwork(beta, state_size, 1, layer1_dims, layer_2_dims )

        self.softplus = T.nn.Softplus()
                 
    def action(self, observation):
        mu, sigma = self.actor.forward(observation)
        sigma = self.softplus(sigma) + 0.001
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

        (actor_loss + critic_loss).backward()

        self.actor.optimizer.step()
        self.critic.optimizer.step()


def Run(screen : PG.Surface, clock : PG.time.Clock, cars : Car.Cars, map : np.ndarray, max_runs=-1):
    surface = PG.surfarray.make_surface(map)

    power_ac1 = ActorCritic(0.0001, 0.0005, 0.99, action_size=1, state_size=6,
                            layer1_dims=16, layer_2_dims=8)
    steer_ac1 = ActorCritic(0.0001, 0.0005, 0.99, action_size=1, state_size=6, 
                            layer1_dims=16, layer_2_dims=8)
             
    power_ac2 = ActorCritic(0.0001, 0.0005, 0.99, action_size=1, state_size=6,
                            layer1_dims=32, layer_2_dims=16)
    steer_ac2 = ActorCritic(0.0001, 0.0005, 0.99, action_size=1, state_size=6, 
                           layer1_dims=32, layer_2_dims=16)

    power_ac3 = ActorCritic(0.0001, 0.0005, 0.99, action_size=1, state_size=6,
                            layer1_dims=128, layer_2_dims=16)
    steer_ac3 = ActorCritic(0.0001, 0.0005, 0.99, action_size=1, state_size=6, 
                           layer1_dims=128, layer_2_dims=16)
    runs = 0
    while runs < max_runs or max_runs == -1:
        cars.reset()

        last_reward = 0
        obs = np.zeros([cars.count,6])
        while cars.any_alive():
            screen.blit(surface, (0,0))
            cars.draw(screen)

            for event in PG.event.get():
                if event.type == PG.QUIT:
                    sys.exit(0)


            a1 = power_ac1.action(obs[0])
            b1 = steer_ac1.action(obs[0])
            a2 = power_ac2.action(obs[1])
            b2 = steer_ac2.action(obs[1])
            a3 = power_ac3.action(obs[2])
            b3 = steer_ac3.action(obs[2])
            
            inputs = np.array([[a1,b1],
                               [a2,b2],
                               [a3,b3]])

            cars.input_controller(inputs)
            cars.update()
            next_obs = cars.observation(screen, False)

            # reward calc needs to improve
            # reward = cars.calc_fitness() - last_reward
            reward = cars.calc_fitness_immediate()
            print(reward)

            power_ac1.learn(obs[0], reward[0], next_obs[0], not cars.alive_list[0])
            steer_ac1.learn(obs[0], reward[0], next_obs[0], not cars.alive_list[0])
                                                         
            power_ac2.learn(obs[1], reward[1], next_obs[1], not cars.alive_list[1])
            steer_ac2.learn(obs[1], reward[1], next_obs[1], not cars.alive_list[1])
                                                         
            power_ac3.learn(obs[2], reward[2], next_obs[2], not cars.alive_list[2])
            steer_ac3.learn(obs[2], reward[2], next_obs[2], not cars.alive_list[2])

            PG.display.flip()
            # clock.tick(60)

            obs = next_obs
            last_reward = reward
        print(runs, cars.calc_fitness())

