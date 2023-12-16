#!/usr/bin/env python3

from __future__ import annotations

import pygame as PG
import numpy as np

class Car:
    # def __init__(self, path="data/carClipArt.jpg", size=50):
    #     # CAR IMAGE
    #     self.orig_image = PG.image.load(path)

    #     w = self.orig_image.get_rect().size[1]
    #     h = self.orig_image.get_rect().size[0]
    #     r = w/h

    #     self.orig_image = PG.transform.scale(self.orig_image, (size,int(size*r)))
    #     self.image = self.orig_image.copy()

    #     # ATTRIBUTES
    #     self.start_position = (0,0)
    #     self.start_rotation = 0
    #     self.start_speed = 3

    #     self.speed = 0
    #     self.min_speed = 2.5

    #     # CURRENT LIFE ATTRIBUTES
    #     self.alive = False
    #     self.life_counter = 0
    #     self.distance = 0
    #     self.info_distance = 0

    #     # TRACK INFO
    #     self.checkpoints = []
    #     self.done_checkpoints = []
    #     self.last_checkpoint = None

    #     # POSITIONAL ATTRIBUTES
    #     self.position = (0,0)
    #     self.rotation = 0

    # def update(self):
    #     ## TODO: LIFE COUNTER
    #     # self.life_counter += 1
    #     # if self.life_counter > 1000:
    #     #     self.alive = False

    #     # CHECK FOR SPEED LIMIT
    #     if self.speed < self.min_speed:
    #         self.speed = self.min_speed

    #     # MOVE
    #     dx = (self.speed * np.cos(np.radians(self.rotation)))
    #     dy = (self.speed * np.sin(np.radians(self.rotation)))

    #     self.distance += np.sqrt(dx**2 + dy**2)
    #     self.info_distance = self.distance
        
    #     self.position = (self.position[0] + dx, self.position[1] - dy)

    # def draw(self, screen, best):
    #     ''' PYGAME DRAWING '''
    #     if self.alive:
    #         if best:
    #             image.fill((255, 0, 0, 255), None, PG.BLEND_RGBA_MULT)
    #             image.fill((100,0,0) + (0,) , None, PG.BLEND_RGBA_ADD)

    #     else:
    #         image.fill((50, 50, 50, 210), None, PG.BLEND_RGBA_MULT)
    #         image.fill((0,0,0) + (0,) , None, PG.BLEND_RGBA_ADD)

    #     screen.blit(image, self.get_center_pos(self.position))

    # def reset(self):
    #     ''' POS/ROT/STATE RESET '''
    #     self.set_pos(self.startPosition)
    #     self.abs_rotate(self.startRotation)
    #     self.speed = self.startSpeed
    #     self.checkpoints = []
    #     self.done_checkpoints = []
    #     self.life_counter = 0

    #     self.distance = 0
    #     self.info_distance = 0
    #     self.alive = True

    # def set_pos(self, pos):
    #     ''' POS SETTER '''
    #     self.position = pos

    # def get_pos(self):
    #     ''' POS GETTER '''
    #     return (int(self.position[0]),int(self.position[1]))

    @staticmethod
    def get_center_pos(pos, image):
        return (int(pos[0] - image.get_width()/2), int(pos[1] - image.get_height()/2))

    # def rel_rotate(self, angle):
    #     ''' ROTATE RELATIVE TO ACTUAL ROT '''
    #     self.rotation += angle
    #     if(self.rotation < -360):
    #         self.rotation += 360
    #     if(self.rotation > 360):
    #         self.rotation -= 360

    #     self.image = PG.transform.rotate(self.orig_image, self.rotation)

    # def abs_rotate(self, angle):
    #     ''' ABSOLUTE ROT/ROT SETTER '''
    #     self.rotation = angle
    #     self.image = PG.transform.rotate(self.orig_image, self.rotation)

    @staticmethod
    def get_corner_points(pos, rotation, image):
        ''' GET CORNER POSITIONS - COLLISION DETECTION '''
        car_height = image.get_height()
        car_width = image.get_width()

        up = np.array([np.cos(np.radians(rotation)), -np.sin(np.radians(rotation))])
        right = np.cross(np.r_[up,0], np.array([0,0,-1]))[:2]

        NN = pos + up*car_height + right*0

        NE = pos + (up*(car_height-5)) + (right*car_width/5)
        NW = pos + (up*(car_height-5)) - (right*car_width/5)

        SE = pos + (up*(-car_height+2)) + (right*car_width/5)
        SW = pos + (up*(-car_height+2)) - (right*car_width/5)

        return up, right, NN, NE, NW, SE, SW

    def collision_detection(self, TRACK_IMAGE, WALL_COLOR, START_COLOR, CHECKPOINT_COLOR):
        ''' COLLISION DETECTION FROM CORNER POINTS '''
        colliders = [WALL_COLOR, START_COLOR, CHECKPOINT_COLOR]
        testPoints = self.get_corner_points()

        for index, p in enumerate(testPoints):
            c = TRACK_IMAGE.get_at(p)

            if(c in colliders or c in CHECKPOINT_COLOR):
                if (c == WALL_COLOR):
                    self.alive = False
                    return -1

                elif (c == START_COLOR and 
                      index == 0 and 
                      self.lastCheckpoint != "START"):

                    self.checkpoints.append(self.life_counter)
                    self.lastCheckpoint = "START"
                    self.done_checkpoints = []
                    self.info_distance = 0
                    return 1

                elif (c in CHECKPOINT_COLOR and 
                      c not in self.done_checkpoints and
                      index == 0):

                    self.checkpoints.append(self.life_counter)
                    self.lastCheckpoint = "CHECK"
                    self.done_checkpoints.append(c)
                    return 2

                else:
                    return 0
        # return code: -1 = wall; 0 = empty; 1 = start; 2 = checkpoint 

    # def calc_fitness(self, life_value, check_value, speed_value, leaderboard):
    #     ''' FULL FITNESS CALCULATION '''
    #     population_size = len(leaderboard)

    #     fitness = 0
    #     fitness += self.distance*life_value
    #     fitness += len(self.checkpoints)*check_value

    #     for loop in range(len(self.checkpoints)):
    #         ch = [_ch for _ch in leaderboard if len(_ch) >= loop+1]

    #         if not (len(ch) > 1): 
    #             fitness += speed_value
    #             continue
                
    #         ch = sorted(ch, key = lambda x: x[loop])

    #         rank = ch.index(self.checkpoints)
    #         fitness += speed_value - rank*(speed_value/len(ch))

    #     return int(fitness)

class Cars:
    def __init__(self, count, start_position, start_rotation):
        self.__init_image()
        self.count = count

        self.positions = np.zeros([count,2])
        self.rotations = np.zeros([count])
        self.speeds = np.zeros([count])

        self.life_counters = np.zeros([count])
        self.distances = np.zeros([count])

        self.alive_list = np.ones([count])
        self.best_id = 0

        # TRACK INFO
        # self.checkpoints = []
        # self.done_checkpoints = []
        # self.last_checkpoint = None

        self.START_POSITION = start_position
        self.START_ROTATION = start_rotation

        self.MIN_SPEED = 2.5
        self.START_SPEED = 3


    def __init_image(self):
        image = PG.image.load("./data/carClipArt.jpg")
        size = 50

        w = image.get_rect().size[1]
        h = image.get_rect().size[0]
        r = w/h

        self.car_image = PG.transform.scale(image, (size,int(size*r)))
        
    def draw(self, screen):
        for i in range(self.count):
            image = self.car_image.copy()
            if self.alive_list[i]:
                if self.best_id == i:
                    image.fill((255, 0, 0, 255), None, PG.BLEND_RGBA_MULT)
                    image.fill((100,0,0) + (0,) , None, PG.BLEND_RGBA_ADD)

            else:
                image.fill((50, 50, 50, 210), None, PG.BLEND_RGBA_MULT)
                image.fill((0,0,0) + (0,) , None, PG.BLEND_RGBA_ADD)

            image = PG.transform.rotate(self.car_image, self.rotations[i])
            screen.blit(image, Car.get_center_pos(self.positions[i], image))


            up, right, NN, NE, NW, SE, SW = Car.get_corner_points(self.positions[i], self.rotations[i], self.car_image) # using orig image

            # PG.draw.line(screen, PG.Color(255,0,0), self.positions[i], self.positions[i]+20*up, 2)
            # PG.draw.line(screen, PG.Color(255,0,0), self.positions[i], self.positions[i]+20*right, 2)

            # PG.draw.circle(screen, PG.Color(255,0,0), NN, 2)
            # PG.draw.circle(screen, PG.Color(255,0,0), NE, 2)
            # PG.draw.circle(screen, PG.Color(255,0,0), NW, 2)
            # PG.draw.circle(screen, PG.Color(255,0,0), SE, 2)
            # PG.draw.circle(screen, PG.Color(255,0,0), SW, 2)

    def update(self):
        self.life_counters += self.alive_list
        self.alive_list[self.life_counters > 1000] = False

        self.best = np.argmax(self.distances)

        # CHECK FOR SPEED LIMIT
        self.speeds[self.speeds < self.MIN_SPEED] = self.MIN_SPEED 

        # MOVE
        dx = (self.speeds *  np.cos(np.radians(self.rotations)))
        dy = (self.speeds * -np.sin(np.radians(self.rotations)))

        self.distances += np.sqrt(dx**2 + dy**2)

        self.positions += np.c_[dx,dy]

    def reset(self, i=None):
        if i is not None:
            raise NotImplementedError

        self.positions[:] = self.START_POSITION
        self.rotations[:] = self.START_ROTATION
        self.speeds[:] = self.START_SPEED

    def input(self, i, input : tuple[bool, bool, bool, bool]):
        if input[0]:
            self.speeds[i] += 0.5
        elif input[1]:
            self.speeds[i] -= 0.5

        if input[2]:
            self.rotations[i] += 1
        elif input[3]:
            self.rotations[i] -= 1
