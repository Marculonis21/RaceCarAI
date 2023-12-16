#!/usr/bin/env python3

# from matplotlib import pyplot as plt
import numpy as np
# import os
# import pickle

from src import BoundaryLoop
from src import CheckpointLoop

import pygame as PG

class App:
    def __init__(self):
        PG.init()
        self.screen = PG.display.set_mode((800,800))
        PG.display.set_caption("RACE CAR AI")
        self.clock = PG.time.Clock()

    def Run(self):
        boundary_map = BoundaryLoop.boundary_loop(self.screen, self.clock)
        checkpoints, start_rotation = CheckpointLoop.checkpoint_loop(self.screen, self.clock, boundary_map)


if __name__ == "__main__":
    app = App()
    app.Run()
    
