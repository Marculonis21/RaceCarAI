#!/usr/bin/env python3

from __future__ import annotations

import pygame as PG
import numpy as np

class RayCaster:
    def __init__(self, test_image : np.ndarray, collider : tuple[int,int,int], max_length = 50):
        self.test_image : np.ndarray         = test_image # IMAGE TO TEST WITH
        self.collider  : tuple[int,int,int] = collider  # COLOR COLLIDERS
        self.max_length : int                = max_length # MAX LENGTH UNITS TO TEST
        self.visible = False

    def cast(self, start, angle, screen, resolution = 1) -> tuple[bool, int, tuple[int,int]]:
        _x = np.cos(np.radians(angle))
        _y = np.sin(np.radians(angle))

        dir = np.array([_x,_y])

        dir = dir/np.linalg.norm(dir, axis=-1, keepdims=True)

        roundTemp = (0,0)
        for step in range(1,self.max_length//resolution):
            test = start + dir*(resolution*step)

            # temp = (temp[0] + X_step, temp[1] - Y_step)
            roundTemp = (int(test[0]),int(test[1]))
            if roundTemp[0] < 0 or roundTemp[0] >= self.test_image.shape[0] or \
               roundTemp[1] < 0 or roundTemp[1] >= self.test_image.shape[1]:
                continue

            if (self.test_image[roundTemp[0],roundTemp[1], :] == self.collider).all():
                if self.visible:
                    PG.draw.line(screen, PG.Color("white"), start, roundTemp)
                    PG.draw.circle(screen, PG.Color("red"), roundTemp, 3, 0)

                return (True, step*resolution, roundTemp)

        if self.visible:
            PG.draw.line(screen, PG.Color("white"), start, roundTemp)
            PG.draw.circle(screen, PG.Color("white"), roundTemp, 3, 0)
        return (False, self.max_length, (0,0))
