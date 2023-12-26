#!/usr/bin/env python

import random
from collections import deque
import tensorflow as tf
import numpy as np
import gym
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import Sequential
from tensorflow.nn import relu
from tensorflow.keras.optimizers import Adam
from keras.models import model_from_json
import pickle
import matplotlib.pyplot as plt

class DeepQLearningAgent:
    def __init__(self, num_inputs, num_outputs, batch_size = 8, num_batches = 16):
        self.num_inputs = num_inputs # state size
        self.num_outputs = num_outputs # action size
        
        self.batch_size = batch_size
        self.num_batches = num_batches
        
        self.epsilon = 1.0 
        self.epsilon_decay = 0.995      
        self.gamma = 0.95
        
        self.memory = deque(maxlen=2000)
        self.build_model()
        self.epsilon_min = 0.01
                 
    def build_model(self):
        self.model = Sequential([])
        self.model.add(Dense(24, activation=relu, input_dim=self.num_inputs, name='dense_11'))
        self.model.add(Dense(24, activation=relu))
        self.model.add(Dense(self.num_outputs, activation='linear'))
        
        opt = tf.keras.optimizers.Adam(lr=0.001)
        self.model.compile(optimizer=opt, loss='mse')
    
    def action(self, state, train=False):
        if train and np.random.uniform() < self.epsilon:
            return np.random.randint(self.num_outputs)
        else: 
            return np.argmax(self.model.predict(state)[0])

# Q net predicts q-values from current state -> output is the qvalue that
# corresponds to the action selected from current state
#
# Target net predicts all q-values from next state (after applying action in
# current state) -> outputs all q-values (selects maximum).
#
# ALL Q-values of QNet are left unchanged other than the corresponding q-value
# which changes its value by calc: R + Gamma*max(Target_net_q-value)*(1-done)
#
# Loss is a MSE between Q net output q-value and Target value after calculation
#
# fit does BP with this loss (or fit on current states and improved predicted
#                             values)

    def train(self):
        for _ in range(self.num_batches):
            
            # samplovani minibatche z pameti
            batch = random.sample(self.memory, self.batch_size)
            states = np.array([s for (s, _, _, _, _) in batch])
            next_states = np.array([ns for (_, _, _, ns, _) in batch])
            states = states.reshape((-1, self.num_inputs))
            next_states = next_states.reshape((-1, self.num_inputs))
            
            # predikce odmen za akce
            predicted = self.model.predict(states) # should be Q NET
            next_predicted = self.model.predict(next_states) # should be TARGET NET
                           


            # spocteni cilove hodnoty
            for i, (state, action, reward, next_state, done) in enumerate(batch):
                predicted[i][action] = reward
                if not done:
                    predicted[i][action] = reward + self.gamma*np.amax(next_predicted[i])

            self.model.fit(states, predicted, epochs=1, verbose=0)
                           
        # snizeni epsilon pro epsilon-greedy strategii
        if self.epsilon > self.epsilon_min:
            self.epsilon = self.epsilon*self.epsilon_decay
    
    def memorize(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
        
    def save_model(self):
        model_json = self.model.to_json()
        
        with open("model.json", "w") as json_file:
            json_file.write(model_json)
            
        self.model.save_weights("model.h5")
    
    def load_model(self): 
        json_file = open('model.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        
        loaded_model = model_from_json(loaded_model_json)
        loaded_model.load_weights("model.h5")
        
        self.model = loaded_model

agent = DeepQLearningAgent(...,...)
env = gym.make("CartPole-v1")
rewards = []

for i in range(1001):
    obs = env.reset()
    obs = np.reshape(obs, newshape=(1, -1))
    done = False
    R = 0
    t = 0
    while not done:
        old_state = obs
        action = agent.action(obs, train=True)
        obs, r, done, _ = env.step(action)
        R += r
        t += 1
        r = r if not done else 10 # bonus za uplne vyreseni
        obs = np.reshape(obs, newshape=(1, -1))
        agent.memorize(old_state, action, r, obs, done)
    agent.train()
    
    rewards.append(R)
    if i % 100 == 0:
        print(i, R)
agent.save_model()

open_file = open('rewards.txt', "wb")
pickle.dump(rewards, open_file)
open_file.close()
