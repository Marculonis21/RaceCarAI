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

import pygame as PG

import functools

class App:
    def __init__(self):
        PG.init()
        self.screen = PG.display.set_mode((800,800))
        PG.display.set_caption("RACE CAR AI")
        self.clock = PG.time.Clock()

    def Run(self):
        boundary_map = BoundaryLoop.boundary_loop(self.screen, self.clock)
        map, checkpoints, start_position, start_rotation = CheckpointLoop.checkpoint_loop(self.screen, self.clock, boundary_map)

        data = WorldData.World(map, checkpoints, start_position, start_rotation)

        cars = Car.Cars(50, data)
        # surface = PG.surfarray.make_surface(map)
        ga = GA.GA(50)
        evaluate = functools.partial(EvaluateLoop.evaluate_loop, 
                                     screen=self.screen, clock=self.clock,
                                     cars=cars,
                                     controller=Controller.NetController(),
                                     map=map)

        ga.evolutionary_algorithm(evaluate,50)

        # EvaluateLoop.evaluate_loop(self.screen, self.clock, cars, pop, Controller.NetController(), map)

        # while True:
        #     self.screen.blit(surface, (0,0))

        #     cars.draw(self.screen)

        #     for event in PG.event.get():
        #         if event.type == PG.QUIT:
        #             sys.exit(0)

        #     keys = PG.key.get_pressed()  # Checking pressed keys
        #     cars.input(0, (keys[PG.K_UP], keys[PG.K_DOWN], keys[PG.K_LEFT], keys[PG.K_RIGHT]))
        #     # cars.input(0, (keys[PG.K_UP], keys[PG.K_DOWN], keys[PG.K_LEFT], keys[PG.K_RIGHT]))

        #     cars.update(map, checkpoints)

        #     PG.display.flip()
        #     self.clock.tick(60)

if __name__ == "__main__":
    app = App()
    app.Run()
    
