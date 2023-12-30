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

import pygame as PG

import functools

import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--save", default=None, type=str, help="Save created track - uses argument as save name (then exits)")
parser.add_argument("--load", default=None, type=str, help="Load saved track data")
parser.add_argument("--print_saved", default=False, action="store_true", help="Print all track save names")
parser.add_argument("--draw", default=False, action="store_true", help="Enable track and car drawing")

class App:
    def __init__(self):
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
                sys.exit()

        if args.print_saved:
            print("TODO")
            sys.exit()

        # cars = Car.Cars(50, data)
        # ga = GA.GA(cars.count)
        # evaluate = functools.partial(EvaluateLoop.evaluate_loop, 
        #                              screen=self.screen, clock=self.clock,
        #                              cars=cars,
        #                              controller=Controller.NetController(),
        #                              map=data.map)

        # ga.evolutionary_algorithm(evaluate, gen_count=100)

        # cars = Car.Cars(10, data)
        # cars = Car.Cars(1, data)
        # AC.Run(self.screen, self.clock, cars, data.map) 
        # DDPG.Run(self.screen, self.clock, cars, data.map) 

if __name__ == "__main__":
    app = App()
    args = parser.parse_args()
    app.Run(args)
    
