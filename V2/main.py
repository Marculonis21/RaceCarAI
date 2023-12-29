#!/usr/bin/env python3

# from matplotlib import pyplot as plt
import numpy as np
# import os
# import pickle

from src import BoundaryLoop
from src import CheckpointLoop
from src import Car
from src import GA
from src import WorldData
from src import EvaluateLoop
from src import Controller
from src import AC
from src import DDPG

import pygame as PG

import functools

class App:
    def __init__(self):
        PG.init()
        self.screen = PG.display.set_mode((800,800))
        PG.display.set_caption("RACE CAR AI")
        self.clock = PG.time.Clock()

    def Run(self):
        # boundary_map = BoundaryLoop.boundary_loop(self.screen, self.clock)
        # map, checkpoints, start_position, start_rotation = CheckpointLoop.checkpoint_loop(self.screen, self.clock, boundary_map)

        # data = WorldData.World(map, checkpoints, start_position, start_rotation)

        # WorldData.World.save(data, "track1")
        # quit()
        data = WorldData.World.load("track1")

        # cars = Car.Cars(50, data)
        # # surface = PG.surfarray.make_surface(map)
        # ga = GA.GA(50)
        # evaluate = functools.partial(EvaluateLoop.evaluate_loop, 
        #                              screen=self.screen, clock=self.clock,
        #                              cars=cars,
        #                              controller=Controller.NetController(),
        #                              map=data.map)

        # ga.evolutionary_algorithm(evaluate,50)

        # cars = Car.Cars(10, data)
        cars = Car.Cars(1, data)
        # AC.Run(self.screen, self.clock, cars, data.map) 
        DDPG.Run(self.screen, self.clock, cars, data.map) 

if __name__ == "__main__":
    app = App()
    app.Run()
    
