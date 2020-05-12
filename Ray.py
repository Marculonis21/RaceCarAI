#!/usr/bin/env python3

import pygame as PG
import math

class Ray:
    def __init__(self, testImage, start, angleDir, resolution = 1,maxLenght = 50, visible = False):
        self.testImage = testImage
        self.start = start
        self.angleDir = angleDir
        self.resolution = resolution
        self.maxLenght = maxLenght
        self.visible = visible
