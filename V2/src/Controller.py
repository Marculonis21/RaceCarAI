#!/usr/bin/env python3

from abc import ABC, abstractmethod
import numpy as np

class Controller(ABC):
    @abstractmethod
    def action(self,pop, observation) -> np.ndarray:
        pass

class NetController(Controller):
    def action(self,pop, observation):
        out = []
        for ind in range(len(pop)):
            x = observation[ind]
            for layer in range(pop[ind].shape[0]):
                y1 = np.tanh(x@pop[ind,layer])
                x = y1
            out.append(x)

        return np.array(out,dtype=object)
