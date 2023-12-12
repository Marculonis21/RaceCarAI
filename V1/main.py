#!/usr/bin/env python3

from matplotlib import pyplot as plt
import math
import numpy as np
import os
import pickle
import pygame as PG
import sys
 
from Boundary import Boundary
from Boundary import Checkpoint
from Boundary import CircleBoundary as CBoundary
from Car import Car
from GeneticAlg import GeneticAlg
from Ray import RayCaster
import Controller as Ctrl

# FIGURE PLOT
def plotValues(v1, v2, v3):
    plt.cla()

    plt.plot(v1) 
    plt.plot(v2) 
    plt.plot(v3)

# STATE MODES
MODE = 0
TRACKDRAWING = 0
SETUP = 1
TRAINING = 2

# PYGAME
PG.init()
PG.font.init()
fontHeader = PG.font.SysFont('Calibri', 35, True, False)
fontText = PG.font.SysFont('Calibri', 25, False, False)

screen = PG.display.set_mode((800,800))
PG.display.set_caption("RACE CAR AI")
clock = PG.time.Clock()

#----------------------------------------------------DRAWING STUFF-------|

BRUSH_RADIUS = 20
WALL_COLOR = (100,100,100)
START_COLOR = (255,200,200)
CHECKPOINT_COLOR = (200,200,255)
CHECKPOINT_COLOR = []

#----------------------------------------------------NETWORK-------------|

NETWORK_ARCHITECTURE = [6,8,4,2] 

test_iteration = 0 
test_mainIter = 0
test_change = True

testing = False
test_episodes = 50
TESTING_ARCHITECTURE = [[6,8,4,2],
                       [6,10,5,2],
                       [6,16,8,2]]

#----------------------------------------------------TRACK STUFF---------|

TRACK_IMAGE = None
boundaries = []
START_POSITION = (0,0) 
START_ROTATION = 0
RAY_VISIBILITY = False

SETUPMODE = 0 #0 START; #1 START_ROTATION; 2 CHECKPOINTS 
checkpoints = []

#----------------------------------------------------GENETIC ALG---------|

POPULATION_SIZE = 50

#----------------------------------------------------MAIN LOOP-----------|

while True:
    screen.fill((50,50,50))

    for b in boundaries:
        b.update()
    for c in checkpoints:
        c.update()

#----------------------------------------------------INPUT OPTIONS-------|

    # INPUT EVENTS
    for event in PG.event.get():
        if event.type == PG.QUIT: sys.exit()

        if event.type == PG.KEYUP:

            # EXIT - ESCAPE
            if event.key == PG.K_ESCAPE:
                try:
                    plt.savefig("./saves/ended-e{}-{}-max{}.png".format(len(episodes[0]),str(NETWORK_ARCHITECTURE), max_fit))
                except:
                    pass

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
                    if(BRUSH_RADIUS < 100):
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
                                START_POSITION = ((p1[0] + p2[0])//2, (p1[1]+p2[1])//2)

                                checkpoints.append(Checkpoint(screen, START_COLOR, p1, p2))

                                SETUPMODE = 1

                            elif (SETUPMODE == 1):
                                mPos = PG.mouse.get_pos()
                                dx = START_POSITION[0] - mPos[0]
                                dy = START_POSITION[1] - mPos[1]
                                rads = math.atan2(-dy,dx)
                                rads %= 2*math.pi
                                degs = math.degrees(rads) + 180

                                START_ROTATION = degs

                                SETUPMODE = 2

                            elif(SETUPMODE == 2):
                                color = (200,200,255-len(checkpoints))
                                CHECKPOINT_COLOR.append(color)
                                checkpoints.append(Checkpoint(screen, color, p1, p2))


            if event.type == PG.KEYUP:
                # SETUP ADD START 
                if event.key == PG.K_KP1 or event.key == 43:
                    SETUPMODE = 0

                # SETUP ADD CHECKPOINTS
                if event.key == PG.K_KP2 or event.key == 236:
                    SETUPMODE = 2

                # SETUP CLEAR - N
                if event.key == PG.K_n:
                    SETUPMODE = 0
                    checkpoints = []

                # REMOVE LAST CHECPOING - B
                if event.key == PG.K_b:
                    checkpoints.pop()
                    if(len(checkpoints) == 0):
                        SETUPMODE = 0

                # CAPTURE SCREEN -> TRAINING - ENTER 
                if event.key == PG.K_RETURN and len(checkpoints) > 0 and SETUPMODE != 1:
                # if event.key == PG.K_RETURN:
                    PG.image.save(screen, "data/track.png")
                    TRACK_IMAGE = PG.image.load("data/track.png")

                    carList = [Car("data/carClipArt.jpg", 50) for car in range(POPULATION_SIZE)]

                    # CAR PREPARATION
                    for car in carList:
                        car.startPosition = START_POSITION
                        car.startRotation = START_ROTATION
                        car.checkpoints = [0 for i in range(len(checkpoints))]
                        car.reset()

                    if not (testing):
                        GA = GeneticAlg(POPULATION_SIZE, 0.025)
                        for item in GA.population:

                            NN = NETWORK_ARCHITECTURE 
                            for layer in range(len(NN)):
                                if (layer == len(NN) - 1): break
                                    
                                w = 2*np.random.random([NN[layer], NN[layer + 1]]) - 1
                                _w = list(w)
                                for y in range(len(_w)):
                                    for x in range(len(_w[0])):
                                        item.append(_w[y][x])
                            
                    plt.style.use('ggplot')
                    episodes = [[],[],[]]
                    MODE = TRAINING

                # BACK TO TRACK DRAWING - BACKSPACE
                if event.key == PG.K_BACKSPACE:
                    SETUPMODE = 0
                    checkpoints = []

                    MODE = TRACKDRAWING

        elif(MODE == TRAINING):
            if event.type == PG.KEYUP:
                # CAR RAY_VISIBILITY
                if event.key == PG.K_p:
                    RAY_VISIBILITY = not RAY_VISIBILITY
                

#----------------------------------------------------STATE MACHINE-------|
#----------------------------------------------------TRACKDRAW STATE-----|

    if(MODE == TRACKDRAWING):
        aPos = PG.mouse.get_pos()
        PG.draw.circle(screen, PG.Color('white'), aPos, BRUSH_RADIUS, 1)

        # text = ["Right click - Draw walls",
        #         "Left click - Erase walls",
        #         "Mouse wheel - Change brush size",
        #         "N - Remove all walls"]
        text = ["Pravé tlačítko myši - Přidat stěny",
                "Levé tlačítko myši - Mazat stěny",
                "Kolečko myši - Změnit velikost štětce",
                "N - Smazat vše"]

        # textsurface = fontHeader.render("Track Drawing:", True, (230,230,255))
        textsurface = fontHeader.render("Nakreslit trať:", True, (230,230,255))
        screen.blit(textsurface, (10,10))

        for index, t in enumerate(text):
            textsurface = fontText.render(t, True, PG.Color('white'))
            screen.blit(textsurface, (12,40+25*index))


#----------------------------------------------------TRACKSETUP STATE----|

    elif(MODE == SETUP):
        # text = ["Right click - Add checkpoint to track",
        #         "1 - Add start",
        #         "2 - Add checkpoints",
        #         "B - Remove last checkpoint",
        #         "N - Remove all checkpoints"]
        text = ["Pravé tlačítko myši - bod",
                "1 - Přidat start",
                "2 - Přidat záchytný bod",
                "B - Vymazat poslední vložený bod",
                "N - Vymazat všechny body",
                "",
                "Backspace - Vrátit se zpět ke kreslení"]

        # textsurface = fontHeader.render("Track Setup:", True, (230,230,255))
        textsurface = fontHeader.render("Připravit trať:", True, (230,230,255))
        screen.blit(textsurface, (10,10))

        # SETUPMODE = 1 - START DIR
        if (SETUPMODE == 1):
            PG.draw.line(screen, (255,100,100), START_POSITION, PG.mouse.get_pos(), 3)

            mPos = PG.mouse.get_pos()
            dx = START_POSITION[0] - mPos[0]
            dy = START_POSITION[1] - mPos[1]
            rads = math.atan2(-dy,dx)
            rads %= 2*math.pi
            degs = math.degrees(rads) + 180

            X_1 = mPos[0] + (math.cos(math.radians(degs + 225)) * 20)
            Y_1 = mPos[1] - (math.sin(math.radians(degs + 225)) * 20)
            X_2 = mPos[0] + (math.cos(math.radians(degs + 135)) * 20)
            Y_2 = mPos[1] - (math.sin(math.radians(degs + 135)) * 20)

            PG.draw.line(screen, (255,100,100), PG.mouse.get_pos(), (X_1,Y_1), 3)
            PG.draw.line(screen, (255,100,100), PG.mouse.get_pos(), (X_2,Y_2), 3)
            
        for index, t in enumerate(text):
            if((index == 1) and (SETUPMODE == 0 or SETUPMODE == 1)):
                textsurface = fontText.render(t, True, (255,200,200))
            elif(index == 2 and SETUPMODE == 2):
                textsurface = fontText.render(t, True, (200,200,255))
            else:
                textsurface = fontText.render(t, True, PG.Color('white'))
            screen.blit(textsurface, (14,40+25*index))

#----------------------------------------------------TRAINING STATE------|

    elif(MODE == TRAINING):

        # ARCHITECTURE TESTING
        if (testing and test_change):
            print("Iter: {}".format(test_mainIter))

            GA = GeneticAlg(POPULATION_SIZE, 0.025)
            for item in GA.population:
                NN = TESTING_ARCHITECTURE[test_iteration]

                for layer in range(len(NN)):
                    if (layer == len(NN) - 1): break
                        
                    w = 2*np.random.random([NN[layer], NN[layer + 1]]) - 1
                    _w = list(w)
                    for y in range(len(_w)):
                        for x in range(len(_w[0])):
                            item.append(_w[y][x])

            test_mainIter += 1
            if (test_mainIter == 2):
                test_mainIter = 0
                test_iteration += 1
                
            test_change = False
                            
        # MAIN CAR-LOOP
        done = True
        best_car = None
        if(carList[0].distance > 0):
            best_current = [c for c in carList if c.alive]
            if(len(best_current) > 0):
                best_car = sorted(best_current, key = lambda x: x.distance).pop()

        for index, car in enumerate(carList):
            if(car.alive):
                done = False

                # INFO = NETWORK INPUT
                info = []
                for i in range(5):
                    angle = -60 + 30*i
                    ray = rayCaster.cast(car.get_corner_points()[0], car.rotation + angle, 2, screen, RAY_VISIBILITY)
                    info.append(ray[1]/200)
                    
                info.append(car.info_distance/500)
                # CONTROLLER
                output = Ctrl.controller(GA.population[index], info, NETWORK_ARCHITECTURE)

                # OUTPUT
                powerOutput = output[0] # up|stable|down
                steerOutput = output[1] # left|front|right

                if (powerOutput > 0.25):
                    car.speed += 0.4 * powerOutput
                elif (powerOutput < -0.25):
                    car.speed += 0.4 * powerOutput
                else:
                    pass

                if (steerOutput > 0.1):
                    car.rel_rotate(5*steerOutput)
                elif (steerOutput < -0.1):
                    car.rel_rotate(5*steerOutput)
                else:
                    pass

                car.update_pos()

                # COLLISION CHECK
                try:
                    car.collision_detection(TRACK_IMAGE, WALL_COLOR, START_COLOR, CHECKPOINT_COLOR)
                except IndexError:
                    car.alive = False

                # # COLLISION POINTS DRAWING
                # for point in car.get_corner_points():
                #     PG.draw.circle(screen, PG.Color('white'), point, 3, 0)

            
            # CAR DRAWING
            car.update(screen, car==best_car)


        # PG.image.save(screen, "./record/pic.png".format(car.life_counter))
        # quit()

        # AFTER ALL DONE
        if (done):
            checkLeaderboard = [car.checkpoints for car in carList]
            for i, car in enumerate(carList):
                GA.fitness[i] = car.calc_fitness(0.75, 50.0, 100.0, checkLeaderboard)
                car.reset()

            last_best, avg_fitness, min_fit, max_fit = GA.new_generation()
            episodes[0].append(avg_fitness)
            episodes[1].append(min_fit)
            episodes[2].append(max_fit)

            plt.cla()
            # plt.title('Training')
            # plt.xlabel('Episode')
            # plt.ylabel('Fitness')
            plt.title('Trénink')
            plt.xlabel('Epizoda')
            plt.ylabel('Zdatnost')
            # plt.plot(episodes[0], label='Average fitness')
            plt.plot(episodes[0], label='Průměrná zdatnost')
            plt.plot(episodes[1], label='Min-zdatnost')
            plt.plot(episodes[2], label='Max-zdatnost')
            plt.legend(loc='upper left', fontsize=9)
            plt.tight_layout()
            plt.pause(0.1)

            # FIGURE SAVING
            while True:
                try:
                    if not (testing):
                        path = str(NETWORK_ARCHITECTURE).replace(" ", "_")
                        saveFile = open("./saves/test-{}/saveFile-e{}-{}-max{}.pickle".format(path,len(episodes[0]),str(NETWORK_ARCHITECTURE),max_fit), "w+b")
                    else:
                        path = str(TESTING_ARCHITECTURE[test_iteration]).replace(" ", "_")
                        saveFile = open("./saves/test-{}/saveFile-iter{}-e{}-{}-max{}.pickle".format(path,test_mainIter,len(episodes[0]),str(TESTING_ARCHITECTURE[test_iteration]),max_fit), "w+b")
                    break
                except:
                    if not (testing):
                        path = str(NETWORK_ARCHITECTURE).replace(" ", "_")
                        os.system('mkdir saves/test-{}'.format(path))
                    else:
                        path = str(TESTING_ARCHITECTURE[test_iteration]).replace(" ", "_")
                        os.system('mkdir saves/test-{}'.format(path))

            pickle.dump(last_best, saveFile)
            saveFile.close()

            if (testing and len(episodes[0]) > test_episodes):
                plt.savefig("./saves/t{}-e{}-{}-max{}.png".format(test_mainIter,len(episodes[0]),str(TESTING_ARCHITECTURE[test_iteration]), max_fit))
                episodes = [[],[],[]]
                test_change = True
                print("NEW ITERATION {}".format(str(TESTING_ARCHITECTURE[test_iteration])))


    # FRAMERATE 60 and REDRAW
    PG.display.flip()
    clock.tick(60)
