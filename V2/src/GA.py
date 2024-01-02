#!/usr/bin/env python3

import numpy as np
import random
import copy

class NetController():
    def action(self,pop, observation):
        out = []
        for ind in range(len(pop)):
            x = observation[ind]
            for layer in range(pop[ind].shape[0]):
                y1 = np.tanh(x@pop[ind,layer])
                x = y1
            out.append(x)

        return np.array(out,dtype=object)

class GA:
    def __init__(self, pop_size):
        self.POP_SIZE = pop_size

        self.NETWORK_ARCHITECTURE = [6,8,4,2]
        self.CROSSOVER_PROB = 0.85

        self.MUT_PROB= 0.025

    def __create_ind(self):
        NN = self.NETWORK_ARCHITECTURE

        ind = []
        for layer in range(len(NN)):
            if layer == len(NN) - 1: break

            w = np.random.uniform(-1, 1, [NN[layer], NN[layer+1]])
            ind.append(w)

        return np.array(ind, dtype=object)

    def create_population(self, size):
        return np.array([self.__create_ind() for _ in range(size)])

    # # tournament selection
    def tournament_selection(self, pop, fits):
        selected = []
        for _ in range(len(pop)):
            i1, i2 = random.randrange(0, len(pop)), random.randrange(0, len(pop))
            if fits[i1] > fits[i2]:
                selected.append(pop[i1])
            else:
                selected.append(pop[i2])
        return selected

    # # roulette wheel selection
    def roulette_wheel_selection(self, pop, fits):
        return random.choices(pop, fits, k=len(pop))

    # one point crossover
    def __cross(self, p1, p2):
        for l1, l2 in zip(p1,p2):
            for i in range(len(l1.ravel())):
                if np.random.random() < 0.5:
                    l1.ravel()[i], l2.ravel()[i] = l2.ravel()[i], l1.ravel()[i]

        return p1, p2

    # applies crossover to all individuals
    def crossover(self, pop):
        off = []
        for p1, p2 in zip(pop[0::2], pop[1::2]):
            o1, o2 = copy.deepcopy(p1), copy.deepcopy(p2)
            if np.random.random() < self.CROSSOVER_PROB:
                o1, o2 = self.__cross(copy.deepcopy(o1),copy.deepcopy(o2))
            off.append(o1)
            off.append(o2)
        return off

    def __mutate(self, p):
        mutant = copy.deepcopy(p)
        for l in range(mutant.shape[0]):
            for i in range(mutant[l].ravel().shape[0]):
                if np.random.random() < self.MUT_PROB:
                    mutant[l].ravel()[i] = np.random.uniform(-1,1)

        return mutant

    # applies mutation to the whole population
    def mutation(self, pop):
        return list(map(self.__mutate, pop))

    # implements the whole EA
    def evolutionary_algorithm(self, fitness, gen_count=-1, visualize=False):
        pop = self.create_population(self.POP_SIZE)
        G = 0
        score_history = []
        while G < gen_count or gen_count == -1:
            fits = fitness(individuals=pop, visualize=visualize)
            score_history.append(fits)

            print(G, np.sum(fits)/self.POP_SIZE, np.max(fits)) # prints fitness to console

            mating_pool = self.roulette_wheel_selection(pop, fits)
            offspring = self.mutation(self.crossover(mating_pool))

            pop = offspring[:-1]+[pop[np.argmax(fits)]] #elitism
            pop = np.array(pop,dtype=object)

            G += 1

        return score_history
