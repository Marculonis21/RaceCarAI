#!/usr/bin/env python3

import pygame as PG
import math

class RayCaster:
    def __init__(self, testImage, collider, resolution = 1, maxLength = 50, visible = False):
        self.testImage = testImage #Image to test against
        self.collider = collider #Color collider
        self.resolution = resolution #Unit-steps to test
        self.maxLength = maxLength #Max units to test
        self.visible = visible

    def cast(self, start, angleDir):
        #start - Start position of the Ray
        #angleDir - Ray angle

        X_step = math.cos(math.radians(angleDir)) * self.resolution
        Y_step = math.sin(math.radians(angleDir)) * self.resolution
        print(angleDir)

        temp = start
        for step in range(self.maxLength//self.resolution):
            temp = (int(round((temp[0] + X_step))),int(round(temp[1] - Y_step)))

            try:
                if(self.testImage.get_at(temp) == self.collider):
                    if(self.visible): return (True, step * self.resolution, temp)
                    else: return (True, step * self.resolution)
            except IndexError:
                pass

        if(self.visible): return (False, self.maxLength, temp)  
        else: return (False, self.maxLength)

