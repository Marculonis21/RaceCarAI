#!/usr/bin/env python3

import pygame as PG

class Boundary:
    def __init__(self, screen, start, end, weight, color):
        self.screen = screen
        self.start = PG.Vector2(start)
        self.end = PG.Vector2(end)
        self.weight = weight
        self.color = color

    def update(self):
         PG.draw.line(self.screen, self.color, self.start, self.end, self.weight)

class CircleBoundary:
    def __init__(self, screen, pos, radius, color):
        self.screen = screen
        self.pos = pos
        self.radius = radius
        self.color = color

    def update(self):
        PG.draw.circle(self.screen, self.color, self.pos, self.radius)
