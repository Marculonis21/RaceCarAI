#!/usr/bin/env python3

# from matplotlib import pyplot as plt
import numpy as np
# import os
# import pickle

from src import BoundaryLoop
from src import CheckpointLoop
from src import Car

import pygame as PG

import sys

class App:
    def __init__(self):
        PG.init()
        self.screen = PG.display.set_mode((800,800))
        PG.display.set_caption("RACE CAR AI")
        self.clock = PG.time.Clock()

    def Run(self):
        boundary_map = BoundaryLoop.boundary_loop(self.screen, self.clock)
        checkpoints, start_position, start_rotation = CheckpointLoop.checkpoint_loop(self.screen, self.clock, boundary_map)

        cars = Car.Cars(1, start_position, start_rotation)
        cars.reset()

        surface = PG.surfarray.make_surface(boundary_map)
        while True:
            self.screen.blit(surface, (0,0))
            for c in checkpoints:
                c.draw()

            for event in PG.event.get():
                if event.type == PG.QUIT:
                    sys.exit(0)

            keys = PG.key.get_pressed()  # Checking pressed keys
            cars.input(0, (keys[PG.K_UP], keys[PG.K_DOWN], keys[PG.K_LEFT], keys[PG.K_RIGHT]))

            cars.update()
            cars.draw(self.screen)

            PG.display.flip()
            self.clock.tick(60)



if __name__ == "__main__":
    app = App()
    app.Run()
    
