#!/usr/bin/env python3

import pygame as PG
import math

class Car:
    def __init__(self, path, size):

        # CAR IMAGE
        self.orig_image = PG.image.load(path)

        w = self.orig_image.get_rect().size[1]
        h = self.orig_image.get_rect().size[0]
        r = w/h

        self.orig_image = PG.transform.scale(self.orig_image, (size,int(size*r)))
        self.image = self.orig_image.copy()


        # ATTRIBUTES
        self.startPosition = (0,0)
        self.startRotation = 0
        self.startSpeed = 3

        self.speed = 0
        self.MIN_speed = 2.5 

        # CURRENT LIFE ATTRIBUTES
        self.alive = False
        self.life_counter = 0
        self.distance = 0
        self.info_distance = 0

        # TRACK INFO
        self.checkpoints = []
        self.done_checkpoints = []
        self.lastCheckpoint = None

        # POSITIONAL ATTRIBUTES
        self.position = (0,0)
        self.rotation = 0


    def update(self, screen):
        ''' PYGAME DRAWING '''
        if(self.alive):
            screen.blit(self.image, self.get_center_pos(self.position))
            self.life_counter += 1
            if(self.life_counter > 1000):
                self.alive = False
        else:
            disabled = self.image.copy()
            disabled.fill((50, 50, 50, 210), None, PG.BLEND_RGBA_MULT)
            disabled.fill((0,0,0) + (0,) , None, PG.BLEND_RGBA_ADD)
            
            screen.blit(disabled, self.get_center_pos(self.position))

    def reset(self):
        ''' POS/ROT/STATE RESET '''
        self.set_pos(self.startPosition)
        self.abs_rotate(self.startRotation)
        self.speed = self.startSpeed
        self.checkpoints = []
        self.done_checkpoints = []
        self.life_counter = 0

        self.distance = 0
        self.info_distance = 0
        self.alive = True

    def update_pos(self):
        ''' CAR MOVEMENT '''
        # CHECK FOR SPEED LIMIT
        if (self.speed < self.MIN_speed):
            self.speed = self.MIN_speed

        # MOVE
        dx = (self.speed * math.cos(math.radians(self.rotation)))
        dy = (self.speed * math.sin(math.radians(self.rotation)))

        self.distance += math.sqrt(dx**2 + dy**2)
        self.info_distance = self.distance
        
        self.position = (self.position[0] + dx,
                         self.position[1] - dy)

    def set_pos(self, pos):
        ''' POS SETTER '''
        self.position = pos

    def get_pos(self):
        ''' POS GETTER '''
        return (int(self.position[0]),int(self.position[1]))

    def get_center_pos(self, pos):
        ''' FOR PYGAME SPRITE ROTATION '''
        return (int(pos[0] - int(self.image.get_width()/2)), int(pos[1] - int(self.image.get_height()/2)))

    def rel_rotate(self, angle):
        ''' ROTATE RELATIVE TO ACTUAL ROT '''
        self.rotation += angle
        if(self.rotation < -360):
            self.rotation += 360
        if(self.rotation > 360):
            self.rotation -= 360

        self.image = PG.transform.rotate(self.orig_image, self.rotation)

    def abs_rotate(self, angle):
        ''' ABSOLUTE ROT/ROT SETTER '''
        self.rotation = angle
        self.image = PG.transform.rotate(self.orig_image, self.rotation)

    def get_corner_points(self):
        ''' GET CORNER POSITIONS - COLLISION DETECTION '''
        car_height = self.orig_image.get_height()
        car_width = self.orig_image.get_width()

        # CORNER ESTIMATION
        angle = 23
        c = math.sqrt((car_height/2)**2 + (car_width/2)**2) - 6 

        xx = math.cos(math.radians(self.rotation)) * car_width/2
        yy = math.sin(math.radians(self.rotation)) * car_width/2

        x1 = math.cos(math.radians(self.rotation-angle)) * c
        y1 = math.sin(math.radians(self.rotation-angle)) * c
        x2 = math.cos(math.radians(self.rotation+angle)) * c
        y2 = math.sin(math.radians(self.rotation+angle)) * c

        x3 = math.cos(math.radians(self.rotation+180-angle)) * c
        y3 = math.sin(math.radians(self.rotation+180-angle)) * c
        x4 = math.cos(math.radians(self.rotation+180+angle)) * c
        y4 = math.sin(math.radians(self.rotation+180+angle)) * c

        center_pos = self.position
        NN = (int(center_pos[0] + xx), int(center_pos[1] - yy))

        NE = (int(center_pos[0] + x1), int(center_pos[1] - y1))
        NW = (int(center_pos[0] + x3), int(center_pos[1] - y3))
        SE = (int(center_pos[0] + x2), int(center_pos[1] - y2))
        SW = (int(center_pos[0] + x4), int(center_pos[1] - y4))

        return (NN,NE,SE,NW,SW)

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

    def calc_fitness(self, life_value, check_value, speed_value, leaderboard):
        ''' FULL FITNESS CALCULATION '''
        population_size = len(leaderboard)

        fitness = 0
        fitness += self.distance*life_value
        fitness += len(self.checkpoints)*check_value

        for loop in range(len(self.checkpoints)):
            ch = [_ch for _ch in leaderboard if len(_ch) >= loop+1]

            if not (len(ch) > 1): 
                fitness += speed_value
                continue
                
            ch = sorted(ch, key = lambda x: x[loop])

            rank = ch.index(self.checkpoints)
            fitness += speed_value - rank*(speed_value/len(ch))

        return int(fitness)
