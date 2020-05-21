#!/usr/bin/env python3

import pygame as PG
import sys
import random

from Boundary import Boundary
from Boundary import CircleBoundary as CBoundary
from Boundary import Checkpoint
from Car import Car
from Ray import RayCaster

MODE = 0
TRACKDRAWING = 0
SETUP = 1
TRAINING = 2

PG.init()
PG.font.init()
fontHeader = PG.font.SysFont('Calibri', 35, True, False)
fontText = PG.font.SysFont('Calibri', 25, False, False)

screen = PG.display.set_mode((800,800))
PG.display.set_caption("RACE CAR AI")
clock = PG.time.Clock()

BRUSH_RADIUS = 20
WALL_COLOR = (100,100,100)
START_COLOR = (255,200,200)
CHECKPOINT_COLOR = (200,200,255)

TRACK_IMAGE = None
boundaries = []
START_ROTATION = 0

SETUPMODE = 0 #0 START; 1 CHECKPOINTS 
checkpoints = []

carList = [Car("data/carClipArt.jpg",50) for car in range(1)]
# for car in carList: 
#     car.speed = 3 
#     car.startPosition = (random.randint(200,400),random.randint(200,400))
#     car.set_pos(car.startPosition)

while True:
    screen.fill((50,50,50))

    for b in boundaries:
        b.update()

    for c in checkpoints:
        c.update()

    # INPUT EVENTS
    for event in PG.event.get():
        if event.type == PG.QUIT: sys.exit()

        if event.type == PG.KEYUP:

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

            if event.type == PG.KEYUP:
                # BOUNDARY CLEAR - N
                if event.key == PG.K_n:
                    boundaries = []

                # END TRACK DRAWING -> TRACK SETUP - ENTER
                if event.key == PG.K_RETURN:
                    PG.image.save(screen, "data/track.png")
                    TRACK_IMAGE = PG.image.load("data/track.png")

                    rayCaster = RayCaster(TRACK_IMAGE,
                                          WALL_COLOR, 
                                          maxLength=200)

                    MODE = SETUP

        elif(MODE == SETUP):
            if event.type == PG.MOUSEBUTTONDOWN:
                # ADDING CHECKPOINTS
                if event.button == 1:
                    rays = []
                    angle = 0
                    for i in range(60):
                        angle += 6
                        rayInfo = [angle, rayCaster.cast(PG.mouse.get_pos(),angle,resolution=2)]
                        if(rayInfo[1][0]):
                            rays.append(rayInfo)

                    if(len(rays) > 0):
                        rays = sorted(rays, key=lambda x: x[1][1])
                        fRay = rays[0]

                        p1 = fRay[1][2]
                        ray = rayCaster.cast(p1,fRay[0]+180,resolution=2) 
                        if(len(ray) > 2):
                            p2 = ray[2]

                            if(SETUPMODE == 0): # START
                                checkpoints = []
                                START_ROTATION = fRay[0] - 90 # LEFT
                                checkpoints.append(Checkpoint(screen, (255,200,200), p1, p2))
                            else:
                                checkpoints.append(Checkpoint(screen, (200,200,255), p1, p2))


            if event.type == PG.KEYUP:
                # SETUP ADD START 
                if event.key == PG.K_KP1:
                    SETUPMODE = 0

                # SETUP ADD CHECKPOINTS
                if event.key == PG.K_KP2:
                    SETUPMODE = 1

                # SETUP CLEAR - N
                if event.key == PG.K_n:
                    checkpoints = []

                # REMOVE LAST CHECPOING - B
                if event.key == PG.K_b:
                    checkpoints.pop()

                # CAPTURE SCREEN -> TRAINING - ENTER 
                if event.key == PG.K_RETURN:
                    PG.image.save(screen, "data/track.png")
                    TRACK_IMAGE = PG.image.load("data/track.png")

                    # PREPARE CARS
                    for car in carList:
                        s = checkpoints[0]
                        car.startPosition = ((s.start[0] + s.end[0])//2, (s.start[1]+s.end[1])//2)
                        car.startRotation = START_ROTATION
                        car.checkpoints = [0 for i in range(len(checkpoints))]
                        car.reset()
                        car.speed = 3

                    MODE = TRAINING

                # BACK TO TRACK DRAWING - BACKSPACE
                if event.key == PG.K_BACKSPACE:
                    SETUPMODE = 0
                    checkpoints = []
                    MODE = TRACKDRAWING

        elif (MODE == TRAINING):
            # KEYBOARD EVENTS
            if event.type == PG.KEYDOWN:
                # PLAYER CONTROL 
                if event.key == PG.K_LEFT:
                    carList[0].rel_rotate(15)
                if event.key == PG.K_RIGHT:
                    carList[0].rel_rotate(-15)

    # INPUT EVENTS


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
                "1 - Add start",
                "2 - Add checkpoints",
                "B - Remove last checkpoint",
                "N - Remove all checkpoints"]

        textsurface = fontHeader.render("Track Setup:", True, (230,230,255))
        screen.blit(textsurface, (10,10))

        for index, t in enumerate(text):
            if(index == 1 and SETUPMODE == 0):
                textsurface = fontText.render(t, True, (255,200,200))
            elif(index == 2 and SETUPMODE == 1):
                textsurface = fontText.render(t, True, (200,200,255))
            else:
                textsurface = fontText.render(t, True, PG.Color('white'))
            screen.blit(textsurface, (14,40+25*index))

    if(MODE == TRAINING):
        for car in carList:
            if(car.alive):
                car.update_pos()
                car.collision_detection(TRACK_IMAGE, WALL_COLOR, START_COLOR, CHECKPOINT_COLOR)
            car.update(screen)

            # CENTER POS je potřeba k vykreslování
            # screen.blit(car.image, car.get_center_pos(car.position))
            # Get_pos je střed auta
            PG.draw.circle(screen, PG.Color('white'), car.get_pos(), 3, 0)

            for point in car.get_corner_points():
                PG.draw.circle(screen, PG.Color('white'), point, 3, 0)

    ## RAYS FOR CHECKPOINTS (PREVIEW)
    # rays = []
    # angle = 0
    # for i in range(60):
    #     angle += 6
    #     rayInfo = [angle, rayCaster.cast(PG.mouse.get_pos(),angle,2,screen,True)]
    #     if(rayInfo[1][0]):
    #         rays.append(rayInfo)

    # if(len(rays) > 0):
    #     rays = sorted(rays, key=lambda x: x[1][1])
    #     fRay = rays[0]

    #     p1 = fRay[1][2]
    #     ray = rayCaster.cast(p1,fRay[0]+180,resolution=2) 
    #     if(len(ray) > 2):
    #         p2 = ray[2]
    #         PG.draw.line(screen, (200,200,255), p1, p2, 5)


    '''
    if(MODE == TRAINING):
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

                rayCast = rayCaster.cast(car.get_corner_points()[0], car.rotation, screen, visible=True)
    '''

    PG.display.flip()

    clock.tick(60)
