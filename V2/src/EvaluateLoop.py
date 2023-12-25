#!/usr/bin/env python3

from __future__ import annotations

from src import Car
from src import Controller
import pygame as PG
import sys
import numpy as np

def evaluate_loop(screen : PG.Surface, clock : PG.time.Clock, cars : Car.Cars, individuals, controller : Controller.Controller, map : np.ndarray):
    surface = PG.surfarray.make_surface(map)

    cars.reset()

    while cars.any_alive():
        screen.blit(surface, (0,0))
        cars.draw(screen)

        for event in PG.event.get():
            if event.type == PG.QUIT:
                sys.exit(0)

        cars.update()

        obs = cars.observation(screen,False)
        actions = controller.action(individuals, obs)
        cars.input_controller(actions)

        PG.display.flip()
        # clock.tick(60)

    return cars.calc_fitness()
