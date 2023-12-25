#!/usr/bin/env python3

from __future__ import annotations
import math

import pygame as PG
import numpy as np

class RayCaster:
    def __init__(self, test_image : np.ndarray, collider : tuple[int,int,int], max_length = 50):
        self.test_image : np.ndarray         = test_image # IMAGE TO TEST WITH
        self.collider  : tuple[int,int,int] = collider  # COLOR COLLIDERS
        self.max_length : int                = max_length # MAX LENGTH UNITS TO TEST
        self.visible = False

    # def cast(self, start, angle, screen=PG.Surface((0,0)), resolution = 1) -> tuple[bool, int, tuple[int,int]]:
    def cast(self, start, angle, screen=PG.Surface((0,0)), resolution = 1) -> tuple[np.ndarray, np.ndarray, np.ndarray]:

        def visualize(end_pos, hit):
            PG.draw.line(screen, PG.Color("white"), tuple(start), end_pos)
            PG.draw.circle(screen, PG.Color("red" if hit else "white"), end_pos, 3, 0)

        _x = np.cos(np.radians(angle))
        _y = np.sin(np.radians(angle))
        dir = np.array([_x,_y])
        dir = dir/np.linalg.norm(dir,axis=0)

        s = np.arange(1, self.max_length//resolution+1)*resolution
        # print(dir.T)
        # print(s)

        out = np.outer(dir.T,s).T
        out = out.reshape(len(s),len(dir[0]),2)

        tests = (np.clip(start + out, 0, self.test_image.shape[0]-1)).astype(np.int16)
        # print(self.test_image[tests[:,:,0], tests[:,:,1]] == self.collider)
        hits = (self.test_image[tests[:,:,0], tests[:,:,1]] == self.collider).all(axis=2).T
        hits_first = np.argmax(hits,axis=1)
        

        if self.visible:
            for id, hit in enumerate(hits_first):
                visualize(tests[hit if hit > 0 else -1, id], hit > 0)

        return (hits_first > 0, hits_first*resolution, tests[hits_first, np.arange(len(dir[0]))])
