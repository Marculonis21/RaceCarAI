#!/usr/bin/env python3

import pygame as PG
import math

class Car:
    def __init__(self, path, size):
        self.orig_image = PG.image.load(path)

        w = self.orig_image.get_rect().size[1]
        h = self.orig_image.get_rect().size[0]
        r = w/h

        self.orig_image = PG.transform.scale(self.orig_image, (size,int(size*r)))
        self.image = self.orig_image.copy()

        self.startPosition = (0,0)
        self.startRotation = 0

        self.alive = False
        self.life_counter = 0

        self.checkpoints = []
        self.check_counter = 0
        self.checkpoint_sleep = 2

        self.position = (0,0)
        self.rotation = 0

        self.speed = 0
        self.wheelDir = 0
        self.MAX_wheelDir = 50

    def update(self, screen):
        ''' PYGAME DRAWING '''
        screen.blit(self.image, self.get_center_pos(self.position))
        if(self.alive):
            self.life_counter += 1

    def reset(self):
        ''' POS/ROT RESET '''
        self.set_pos(self.startPosition)
        self.abs_rotate(self.startRotation)
        self.checkpoints = []
        self.check_counter = 0
        self.alive = True

    def update_pos(self):
        ''' CAR MOVEMENT '''
        self.position = (self.position[0] + (self.speed * math.cos(math.radians(self.rotation))),
                         self.position[1] - (self.speed * math.sin(math.radians(self.rotation))))

    def set_pos(self, pos):
        ''' POS SETTER '''
        self.position = pos

    def get_pos(self):
        ''' POS SETTER '''
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
        ''' ABSOLUTE ROT '''
        self.rotation = angle
        self.image = PG.transform.rotate(self.orig_image, self.rotation)

    def get_corner_points(self):
        ''' GET CORNER POSITIONS - COLLISION DETECTION '''
        car_height = self.orig_image.get_height()
        car_width = self.orig_image.get_width()

        angle = 23
        c = math.sqrt((car_height/2)**2 + (car_width/2)**2) - 6 

        x1 = math.cos(math.radians(self.rotation-angle)) * c
        y1 = math.sin(math.radians(self.rotation-angle)) * c
        x2 = math.cos(math.radians(self.rotation+angle)) * c
        y2 = math.sin(math.radians(self.rotation+angle)) * c

        x3 = math.cos(math.radians(self.rotation+180-angle)) * c
        y3 = math.sin(math.radians(self.rotation+180-angle)) * c

        x4 = math.cos(math.radians(self.rotation+180+angle)) * c
        y4 = math.sin(math.radians(self.rotation+180+angle)) * c

        xx = math.cos(math.radians(self.rotation)) * car_width/2
        yy = math.sin(math.radians(self.rotation)) * car_width/2
        
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

        self.check_counter += 1

        for index, p in enumerate(testPoints):
            c = TRACK_IMAGE.get_at(p)
            if(c in colliders):
                if (c == WALL_COLOR):
                    self.alive = False
                    print("WALL")
                    print(self.checkpoints)
                    return -1
                elif (c == START_COLOR and index == 0 and self.checkpoint_sleep < self.check_counter):
                    self.check_counter = 0
                    self.checkpoints.append(self.life_counter)
                    print("START")
                    print(self.life_counter)
                    return 1
                elif (c == CHECKPOINT_COLOR and index == 0 and self.checkpoint_sleep < self.check_counter):
                    self.check_counter = 0
                    self.checkpoints.append(self.life_counter)
                    print("CHECK")
                    print(self.life_counter)
                    return 2
                else:
                    return 0

        # return code: -1 = wall; 0 = empty; 1 = start; 2 = checkpoint 
