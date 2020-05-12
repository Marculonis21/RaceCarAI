#!/usr/bin/env python3

import pygame as PG
import sys

from Boundary import Boundary
from Boundary import CircleBoundary as CB

PG.init()
screen = PG.display.set_mode((800,800))
PG.display.set_caption("RACE CAR AI")


BRUSH_RADIUS = 20
TRACK_IMAGE = None
boundaries = []
while True:
    screen.fill((50,50,50))

    for b in boundaries:
        b.update()


    for event in PG.event.get():
        if event.type == PG.QUIT: sys.exit()

        #MOUSE BUTTONS EVENTS
        if PG.mouse.get_pressed()[0]:
            aPos = PG.mouse.get_pos()
            boundaries.append(CB(screen, aPos, BRUSH_RADIUS, PG.Color('gray')))

        if PG.mouse.get_pressed()[2]:
            aPos = PG.mouse.get_pos()
            boundaries.append(CB(screen, aPos, BRUSH_RADIUS, (50,50,50)))

        #MOUSE WHEEL EVENTS
        if event.type == PG.MOUSEBUTTONDOWN:
            if event.button == 4:
                if(BRUSH_RADIUS < 50):
                    BRUSH_RADIUS += 1
            elif event.button == 5:
                if(BRUSH_RADIUS > 5):
                    BRUSH_RADIUS -= 1

        #KEYBOARD EVENTS
        if event.type == PG.KEYDOWN:
            if event.key == PG.K_n:
                boundaries = []

            if event.key == PG.K_ESCAPE:
                sys.exit()

            if event.key == PG.K_KP_ENTER:
                PG.image.save(screen, "track.png")
                TRACK_IMAGE = PG.image.load("track.png")

    aPos = PG.mouse.get_pos()
    PG.draw.circle(screen, PG.Color('white'), aPos, BRUSH_RADIUS, 1)

    PG.display.flip()
