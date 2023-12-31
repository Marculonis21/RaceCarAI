#!/usr/bin/env python3


from src import BoundaryLoop
from src import CheckpointLoop
from src import Car
from src import GA
from src import WorldData
from src import EvaluateLoop
from src import Controller
from src import AC
from src import DDPG

import torch

import pygame as PG

import functools
import numpy as np

import argparse
import sys
import os

parser = argparse.ArgumentParser()
parser.add_argument("--save", default=None, type=str, help="Save created track - uses argument as save name (then exits)")
parser.add_argument("--load", default=None, type=str, help="Load saved track data")
parser.add_argument("--print_saved", default=False, action="store_true", help="Print all track save names")
parser.add_argument("--draw", default=False, action="store_true", help="Enable track and car drawing")

REPEATS = 10

class App:
    def __init__(self, args):
        PG.init()
        self.screen = PG.display.set_mode((800,800))
        PG.display.set_caption("RACE CAR AI")
        self.clock = PG.time.Clock()

    def TrackCreation(self) -> WorldData.World:
        boundary_map = BoundaryLoop.boundary_loop(self.screen, self.clock)
        map, checkpoints, start_position, start_rotation = CheckpointLoop.checkpoint_loop(self.screen, self.clock, boundary_map)
        data = WorldData.World(map, checkpoints, start_position, start_rotation)

        return data

    def Run(self, args : argparse.Namespace):
        data = None

        if args.save:
            data = self.TrackCreation()
            WorldData.World.save(data, args.save)
            sys.exit()

        if args.load:
            data = WorldData.World.load(args.load)
            if data is None:
                print("No data loaded - exiting")
                sys.exit()

        if args.print_saved:
            names = [x[:-5] for x in os.listdir("data/user_data/") if x.endswith(".save")]
            print("Save names: ", *names)
            sys.exit()

        assert data is not None

        # run_data = []
        # for i in range(REPEATS):
        #     print(f"GA {i} $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        #     cars = Car.Cars(50, data)
        #     ga = GA.GA(cars.count)
        #     evaluate = functools.partial(EvaluateLoop.evaluate_loop, 
        #                                 screen=self.screen, clock=self.clock,
        #                                 cars=cars,
        #                                 controller=Controller.NetController(),
        #                                 map=data.map)

        #     fits = ga.evolutionary_algorithm(evaluate, gen_count=100, visualize=args.draw)
        #     run_data.append(fits)

#         np.save(f"data/run_data/GA_c50_g100.npy", np.array(run_data))

        # run_data = []
        # for i in range(REPEATS):
        #     print(f"DDPG {i} $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        #     cars = Car.Cars(1, data)
        #     fits = DDPG.Run(self.screen, self.clock, cars, data.map, dims1=64, max_runs=1000, visualize=args.draw) 
        #     run_data.append(fits)

        # np.save(f"data/run_data/DDPG_arch64_64.npy", np.array(run_data))

        run_data = []
        for i in range(REPEATS):
            print(f"DDPG {i} $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            cars = Car.Cars(1, data)
            fits = DDPG.Run(self.screen, self.clock, cars, data.map, dims1=128, max_runs=1000, visualize=args.draw) 
            run_data.append(fits)

        np.save(f"data/run_data/DDPG_arch128_64.npy", np.array(run_data))
            

if __name__ == "__main__":
    args = parser.parse_args()
    app = App(args)
    app.Run(args)
    
