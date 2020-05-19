#!/usr/bin/env python3

import pygame as PG
import sys
import random

from Boundary import Boundary
from Boundary import CircleBoundary as CBoundary
from Boundary import Checkpoint
from Car import Car
from Ray import RayCaster

TRACKDRAWING = 0
SETUP = 1
TRAINING = 2
MODE = 0

PG.init()
PG.font.init()
fontHeader = PG.font.SysFont('Calibri', 35, True, False)
fontText = PG.font.SysFont('Calibri', 25, False, False)

screen = PG.display.set_mode((800,800))
PG.display.set_caption("RACE CAR AI")
clock = PG.time.Clock()

BRUSH_RADIUS = 20
WALL_COLOR = (100,100,100)
TRACK_IMAGE = None
boundaries = []

checkpoints = []

carList = [Car("data/carClipArt.jpg",50) for car in range(1)]
for car in carList: 
    car.speed = 3 
    car.startPosition = (random.randint(200,400),random.randint(200,400))
    car.set_pos(car.startPosition)

while True:
    screen.fill((50,50,50))

    for b in boundaries:
        b.update()

    for c in checkpoints:
        c.update()

    for event in PG.event.get():
        if event.type == PG.QUIT: sys.exit()

        if event.type == PG.KEYDOWN:

            # EXIT - ESCAPE
            if event.key == PG.K_ESCAPE:
                sys.exit()

        if(MODE == TRACKDRAWING):
            # MOUSE BUTTONS EVENTS
            if PG.mouse.get_pressed()[0]:
                aPos = PG.mouse.get_pos()
                boundaries.append(CBoundary(screen, aPos, BRUSH_RADIUS, WALL_COLOR))

            if PG.mouse.get_pressed()[2]:
                aPos = PG.mouse.get_pos()
                boundaries.append(CBoundary(screen, aPos, BRUSH_RADIUS, (50,50,50)))

            # MOUSE WHEEL EVENTS
            if event.type == PG.MOUSEBUTTONDOWN:
                if event.button == 4:
                    if(BRUSH_RADIUS < 50):
                        BRUSH_RADIUS += 1
                elif event.button == 5:
                    if(BRUSH_RADIUS > 5):
                        BRUSH_RADIUS -= 1

            # KEYBOARD EVENTS
            if event.type == PG.KEYDOWN:
                # PLAYER CONTROL 
                if event.key == PG.K_LEFT:
                    carList[0].rel_rotate(30)
                if event.key == PG.K_RIGHT:
                    carList[0].rel_rotate(-30)

                # BOUNDARY CLEAR - N
                if event.key == PG.K_n:
                    boundaries = []


                # END DRAWING START TRAINING - ENTER
                if event.key == PG.K_KP_ENTER:
                    PG.image.save(screen, "data/track.png")
                    TRACK_IMAGE = PG.image.load("data/track.png")

                    RayCaster = RayCaster(TRACK_IMAGE,
                                          WALL_COLOR, 
                                          maxLength=200)

                    MODE = SETUP

        if(MODE == SETUP):
            if event.type == PG.MOUSEBUTTONDOWN:
                # ADDING CHECKPOINTS
                if event.button == 1:
                    rays = []
                    angle = 0
                    for i in range(20):
                        angle += 18
                        rayInfo = [angle, RayCaster.cast(PG.mouse.get_pos(),angle,resolution=2)]
                        if(rayInfo[1][0]):
                            rays.append(rayInfo)

                    if(len(rays) > 0):
                        rays = sorted(rays, key=lambda x: x[1][1])
                        fRay = rays[0]

                        p1 = fRay[1][2]
                        ray = RayCaster.cast(p1,fRay[0]+180,resolution=2) 
                        if(len(ray) > 2):
                            p2 = ray[2]

                            checkpoints.append(Checkpoint(screen, (200,200,255), p1, p2))


            if event.type == PG.KEYDOWN:
                # SETUP CLEAR - N
                if event.key == PG.K_n:
                    checkpoints = []

                if event.key == PG.K_b:
                    checkpoints.pop()


    if(MODE == TRACKDRAWING):
        aPos = PG.mouse.get_pos()
        PG.draw.circle(screen, PG.Color('white'), aPos, BRUSH_RADIUS, 1)

        text = ["Right click - Draw walls",
                "Left click - Erase walls",
                "N - Remove all walls",
                "Mouse wheel - Change brush size"]

        textsurface = fontHeader.render("Track Drawing:", True, (230,230,255))
        screen.blit(textsurface, (10,10))

        for index, t in enumerate(text):
            textsurface = fontText.render(t, True, PG.Color('white'))
            screen.blit(textsurface, (14,40+25*index))

    if(MODE == SETUP):
        text = ["Right click - Add checkpoint to track",
                "B - Remove last checkpoint",
                "N - Remove all checkpoints"]

        textsurface = fontHeader.render("Track Setup:", True, (230,230,255))
        screen.blit(textsurface, (10,10))

        for index, t in enumerate(text):
            textsurface = fontText.render(t, True, PG.Color('white'))
            screen.blit(textsurface, (14,40+25*index))

        # rays = []
        # angle = 0
        # for i in range(60):
        #     angle += 6
        #     rayInfo = [angle, RayCaster.cast(PG.mouse.get_pos(),angle,2,screen,True)]
        #     if(rayInfo[1][0]):
        #         rays.append(rayInfo)

        # if(len(rays) > 0):
        #     rays = sorted(rays, key=lambda x: x[1][1])
        #     fRay = rays[0]

        #     p1 = fRay[1][2]
        #     ray = RayCaster.cast(p1,fRay[0]+180,resolution=2) 
        #     if(len(ray) > 2):
        #         p2 = ray[2]
        #         PG.draw.line(screen, (200,200,255), p1, p2, 5)


    '''
    if(MODE == TRAINING):
        angle = 0
        for i in range(20):
            angle += 18
            raycast = RayCaster.cast(PG.mouse.get_pos(),angle,screen,True)

        for car in carList:
            if(car.rotation < -360):
                car.rotation += 360
            if(car.rotation > 360):
                car.rotation -= 360

            # car.rel_rotate(-2)
            car.update_pos()

            # CENTER POS je potřeba k vykreslování
            screen.blit(car.image, car.get_center_pos(car.position))
            # Get_pos je střed auta
            # PG.draw.circle(screen, PG.Color('white'), car.get_pos(), 5, 0)

            for point in car.get_corner_points():
                PG.draw.circle(screen, PG.Color('white'), point, 5, 0)

                try:
                    if(TRACK_IMAGE.get_at(point) == WALL_COLOR):
                        PG.draw.circle(screen, PG.Color('red'), point, 5, 0)
                    else:
                        PG.draw.circle(screen, PG.Color('white'), point, 5, 0)
                except IndexError:
                    pass

                rayCast = RayCaster.cast(car.get_corner_points()[0], car.rotation, screen, visible=True)
    '''

    PG.display.flip()

    clock.tick(60)
