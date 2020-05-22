#!/usr/bin/env python3

import numpy as np
from GeneticAlg import GeneticAlg

def nonlin(x, deriv=False):
    if(deriv):
        return(x*(1-x)) 

    return 1/(1+np.exp(-x))

def controller(player, observation):
    ''' PLAYER CONTROLLER '''

    w = []
    for y in range(11):
        w.append([])
        for x in range(15):
            w[y].append(player[x+(11*y)])

    w1 = np.array(w)

    w = []
    for y in range(15):
        w.append([])
        for x in range(10):
            w[y].append(player[x+(15*y)])

    w2 = np.array(w)

    w = []
    for y in range(10):
        w.append([])
        for x in range(6):
            w[y].append(player[x+(10*y)])

    w3 = np.array(w)

    l1 = np.array(observation)
    l2 = nonlin(np.dot(l1,w1))
    l3 = nonlin(np.dot(l2,w2))
    l4 = nonlin(np.dot(l3,w3))
    end = l4

    return end
