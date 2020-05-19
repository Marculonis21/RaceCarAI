#!/usr/bin/env python3

import pygame as PG
import math

class RayCaster:
    def __init__(self, testImage, collider, maxLength = 50):
        self.testImage = testImage #Image to test against
        self.collider = collider #Color collider
        self.maxLength = maxLength #Max units to test
        self.visible = False

    def cast(self, start, angleDir, resolution = 1, screen = PG.Surface((0,0)), visible = False):
        #start - Start position of the Ray
        #angleDir - Ray angle

        self.visible = visible
        self.resolution = resolution

        X_step = math.cos(math.radians(angleDir)) * self.resolution
        Y_step = math.sin(math.radians(angleDir)) * self.resolution

        temp = start
        for step in range(self.maxLength//self.resolution):
            temp = (temp[0] + X_step, temp[1] - Y_step)
            roundTemp = ((int(round(temp[0]))),int(round(temp[1])))

            try:
                if(self.testImage.get_at(roundTemp) == self.collider):
                    if(self.visible): 
                        PG.draw.line(screen, PG.Color("white"), start, roundTemp)
                        PG.draw.circle(screen, PG.Color("red"), roundTemp, 5, 0)

                    return (True, step * self.resolution, roundTemp)

            except IndexError:
                pass

        if(self.visible): 
            PG.draw.line(screen, PG.Color("white"), start, roundTemp)
            PG.draw.circle(screen, PG.Color("white"), roundTemp, 5, 0)
        return (False, self.maxLength)
