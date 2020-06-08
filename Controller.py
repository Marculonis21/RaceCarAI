#!/usr/bin/env python3

import numpy as np
from GeneticAlg import GeneticAlg

def sigmoid(x):
    return 1/(1+np.exp(-x))

def tanh(x):
    return np.tanh(x)

def controller(player, observation, network):
    ''' PLAYER CONTROLLER '''

    layer = np.array(observation)

    # FOR ALL LAYERS - PREVIOUS WITH WEIGHTS TO THE NEXT ONE - TILL END
    for l in range(len(network)):
        if (l == len(network) - 1): break
            
        w = []
        for y in range(network[l]):
            w.append([])
            for x in range(network[l+1]):
                w[y].append(player[x+(network[l]*y)])

        w = np.array(w)

        layer = tanh(np.dot(layer,w))

    end = layer

    return end
