#!/usr/bin/env python3

from __future__ import annotations

from src import Car
from src import Controller
import pygame as PG
import sys
import numpy as np

def evaluate_loop(screen : PG.Surface, clock : PG.time.Clock, cars : Car.Cars, individuals, controller : Controller.Controller, map : np.ndarray, visualize):
    surface = PG.surfarray.make_surface(map)

    cars.reset()

    obs = np.zeros([cars.count, 6])
    while cars.any_alive():
        if visualize:
            screen.blit(surface, (0,0))
            cars.draw(screen)

        for event in PG.event.get():
            if event.type == PG.QUIT:
                sys.exit(0)

        actions = controller.action(individuals, obs)
        cars.input_controller(actions)
        cars.update()
        next_obs = cars.observation(screen,False)

        if visualize:
            PG.display.flip()
            # clock.tick(60)

        obs = next_obs

    return cars.calc_fitness()
