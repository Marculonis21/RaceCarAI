#!/usr/bin/env python3

import pygame as PG

class Boundary:
    def __init__(self, start, end, weight, color):
        self.start = PG.Vector2(start)
        self.end = PG.Vector2(end)
        self.weight = weight
        self.color = color

    def draw(self, screen):
        PG.draw.line(screen, self.color, self.start, self.end, self.weight)

class CircleBoundary:
    def __init__(self, pos, radius, color):
        self.pos = pos
        self.radius = radius
        self.color = color

    def draw(self, screen):
        PG.draw.circle(screen, self.color, self.pos, self.radius)

class Checkpoint:
    def __init__(self, color, start, end):
        self.color = color
        self.start = start
        self.end = end
        self.pos = ((start[0] + end[0])//2, (start[1]+end[1])//2)

    def draw(self, screen):
        PG.draw.line(screen, self.color, self.start, self.end, 5)
