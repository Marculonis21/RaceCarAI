#!/usr/bin/env python3

import random as R

class GeneticAlg:
    def __init__(self, popSize, mutRate):
        self.popSize = popSize
        self.mutRate = mutRate

        self.genNumber = 1

        self.population = [[] for size in range(popSize)]
        self.fitness = [-1 for size in range(popSize)]

    def avg_fitness(self):
        ''' AVERAGE FITNESS CALC '''
        sFitness = sum(self.fitness)
        lFitness = len(self.fitness)
        return sFitness/lFitness

    def new_generation(self):
        ''' MAKING NEW GENERATION '''
        self.parents = []
        ordered_pop = [x for _,x in sorted(zip(self.fitness.copy(), self.population.copy()))]
        best = ordered_pop[self.popSize//2:]
        best_one = best[-1]

        best_fit = sorted(self.fitness.copy())[self.popSize//2:]
        
        # PARENTS ROULETTE
        # nMax = sum(self.fitness)
        nMax = sum(best_fit)

        # for i in range(self.popSize):
        for i in range(self.popSize):
            x = R.randint(0,nMax)
            nTest = 0
            for loop in range(self.popSize//2):
                nTest += best_fit[loop]

                if(x <= nTest):
                    self.parents.append(best[loop])
                    break


        # MATING POOL
        self.children = []
        for loop in range(int(self.popSize//2)):
            p1 = R.choice(self.parents)
            self.parents.remove(p1)
            p2 = R.choice(self.parents)
            self.parents.remove(p2)

            ch1 = []
            ch2 = []
            for i in range(len(self.population[0])):
                # CROSSOVER
                x = R.choice([0,1])
                if(x == 0):
                    ch1.append(p1[i])
                    ch2.append(p2[i])
                elif(x == 1):
                    ch1.append(p2[i])
                    ch2.append(p1[i])

            self.children.append(ch1)
            self.children.append(ch2)

        # MUTATION
        for ch in self.children:
            for i in range(len(ch)):
                if(R.random() <= (self.mutRate)):
                    ch[i] = 2*R.random()-1

        # SAVE HALF ADD HALF
        # ordered_pop = [x for _,x in sorted(zip(self.fitness, self.population))]
        # self.population = ordered_pop[self.popSize//2:]
        # self.population = best
        # self.population += (ch for ch in self.children)
        self.population = self.children
        self.population.pop()
        self.population.append(best_one)

        self.genNumber += 1
        return best_one, self.avg_fitness(), min(self.fitness), max(self.fitness)
