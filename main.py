#!/usr/bin/env python3

import pygame as PG
import sys

from Boundary import Boundary
from Boundary import CircleBoundary as CB
from Car import Car

PG.init()
screen = PG.display.set_mode((800,800))
PG.display.set_caption("RACE CAR AI")
clock = PG.time.Clock()

BRUSH_RADIUS = 20
TRACK_IMAGE = None
boundaries = []

car = Car("data/carClipArt.jpg", 100)
car.position = (300,300)
car.rotation = 0

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
                PG.image.save(screen, "data/track.png")
                TRACK_IMAGE = PG.image.load("data/track.png")

    aPos = PG.mouse.get_pos()
    PG.draw.circle(screen, PG.Color('white'), aPos, BRUSH_RADIUS, 1)

    car.speed = 5 
    car.rel_rotate(2)
    car.update_pos()

    #CENTER POS je potřeba k vykreslování
    screen.blit(car.image, car.get_center_pos(car.position))
    #Get_pos je střed auta
    #PG.draw.circle(screen, PG.Color('white'), car.get_pos(), 5, 0)

    print(car.get_corner_points())
    for point in car.get_corner_points():
        PG.draw.circle(screen, PG.Color('white'), point, 5, 0)

    PG.display.flip()

    clock.tick(60)
