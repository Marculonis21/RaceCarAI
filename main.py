#!/usr/bin/env python3

import pygame as PG
import sys
import random

from Boundary import Boundary
from Boundary import CircleBoundary as CB
from Car import Car
from Ray import RayCaster

SETUP = 0
TRAINING = 1

MODE = 0

PG.init()
screen = PG.display.set_mode((800,800))
PG.display.set_caption("RACE CAR AI")
clock = PG.time.Clock()

BRUSH_RADIUS = 20
WALL_COLOR = (100,100,100)
TRACK_IMAGE = None
boundaries = []

carList = [Car("data/carClipArt.jpg",50) for car in range(1)]
for car in carList: 
    car.speed = 0 
    car.startPosition = (random.randint(200,400),random.randint(200,400))
    car.set_pos(car.startPosition)


while True:
    screen.fill((50,50,50))

    for b in boundaries:
        b.update()

    for event in PG.event.get():
        if event.type == PG.QUIT: sys.exit()

        #MOUSE BUTTONS EVENTS
        if PG.mouse.get_pressed()[0]:
            aPos = PG.mouse.get_pos()
            boundaries.append(CB(screen, aPos, BRUSH_RADIUS, WALL_COLOR))

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

            if event.key == PG.K_LEFT:
                carList[0].rel_rotate(5)
            if event.key == PG.K_RIGHT:
                carList[0].rel_rotate(-5)
            if event.key == PG.K_n:
                boundaries = []

            if event.key == PG.K_ESCAPE:
                sys.exit()

            if event.key == PG.K_KP_ENTER:
                PG.image.save(screen, "data/track.png")
                TRACK_IMAGE = PG.image.load("data/track.png")

                RayCaster = RayCaster(TRACK_IMAGE, WALL_COLOR, 5, 200, True)

                MODE = TRAINING

    aPos = PG.mouse.get_pos()
    PG.draw.circle(screen, PG.Color('white'), aPos, BRUSH_RADIUS, 1)

    if(MODE == TRAINING):
        for car in carList:
            if(car.rotation < -360):
                car.rotation += 360
            if(car.rotation > 360):
                car.rotation -= 360

            #car.rel_rotate(-2)
            car.update_pos()

            #CENTER POS je potřeba k vykreslování
            screen.blit(car.image, car.get_center_pos(car.position))
            #Get_pos je střed auta
            #PG.draw.circle(screen, PG.Color('white'), car.get_pos(), 5, 0)

            for point in car.get_corner_points():
                PG.draw.circle(screen, PG.Color('white'), point, 5, 0)

                try:
                    if(TRACK_IMAGE.get_at(point) == WALL_COLOR):
                        PG.draw.circle(screen, PG.Color('red'), point, 5, 0)
                    else:
                        PG.draw.circle(screen, PG.Color('white'), point, 5, 0)
                except IndexError:
                    pass

                rayCast = RayCaster.cast(car.get_corner_points()[0], car.rotation)
                print(rayCast)
                if(RayCaster.visible):
                    try:
                        PG.draw.circle(screen,(PG.Color('red') if rayCast[0] else PG.Color('white')),rayCast[2],5,0)
                        PG.draw.line(screen, PG.Color('white'), car.get_corner_points()[0], rayCast[2])
                    except IndexError:
                        pass
                

    PG.display.flip()

    clock.tick(60)
