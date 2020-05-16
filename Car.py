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

        self.position = (0,0)
        self.rotation = 0

        self.startPosition = (0,0)

        self.speed = 0
        self.wheelDir = 0
        self.MAX_wheelDir = 50

    def get_pos(self):
        return(int(self.position[0]), int(self.position[1]))
    
    def get_center_pos(self, pos):
        return (int(pos[0] - int(self.image.get_width()/2)), int(pos[1] - int(self.image.get_height()/2)))

    def get_corner_points(self):
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
        
        center_pos = self.get_pos()
        NN = (int(center_pos[0] + xx), int(center_pos[1] - yy))

        NE = (int(center_pos[0] + x1), int(center_pos[1] - y1))
        NW = (int(center_pos[0] + x3), int(center_pos[1] - y3))
        SE = (int(center_pos[0] + x2), int(center_pos[1] - y2))
        SW = (int(center_pos[0] + x4), int(center_pos[1] - y4))

        return (NN,NE,SE,NW,SW)


    def rel_rotate(self, angle):
        self.rotation += angle
        self.image = PG.transform.rotate(self.orig_image, self.rotation)

    def abs_rotate(self, angle):
        self.rotation = angle
        self.image = PG.transform.rotate(self.orig_image, self.rotation)

    def update_pos(self):
        self.position = (self.position[0] + (self.speed * math.cos(math.radians(self.rotation))),
                         self.position[1] - (self.speed * math.sin(math.radians(self.rotation))))

    def set_pos(self, pos):
        self.position = pos
