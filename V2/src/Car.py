#!/usr/bin/env python3

import pygame as PG
import numpy as np

class Car:
    def __init__(self, path="data/carClipArt.jpg", size=50):
        # CAR IMAGE
        self.orig_image = PG.image.load(path)

        w = self.orig_image.get_rect().size[1]
        h = self.orig_image.get_rect().size[0]
        r = w/h

        self.orig_image = PG.transform.scale(self.orig_image, (size,int(size*r)))
        self.image = self.orig_image.copy()

        # ATTRIBUTES
        self.start_position = (0,0)
        self.start_rotation = 0
        self.start_speed = 3

        self.speed = 0
        self.min_speed = 2.5

        # CURRENT LIFE ATTRIBUTES
        self.alive = False
        self.life_counter = 0
        self.distance = 0
        self.info_distance = 0

        # TRACK INFO
        self.checkpoints = []
        self.done_checkpoints = []
        self.last_checkpoint = None

        # POSITIONAL ATTRIBUTES
        self.position = (0,0)
        self.rotation = 0

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
    def get_center_pos(pos, img_width, img_height):
        return (int(pos[0] - int(img_width/2)), int(pos[1] - int(img_height/2)))

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
        w = self.car_image.get_width()
        h = self.car_image.get_height()

        for i in range(self.count):
            image = self.car_image.copy()
            if self.alive_list[i]:
                if self.best_id == i:
                    image.fill((255, 0, 0, 255), None, PG.BLEND_RGBA_MULT)
                    image.fill((100,0,0) + (0,) , None, PG.BLEND_RGBA_ADD)

            else:
                image.fill((50, 50, 50, 210), None, PG.BLEND_RGBA_MULT)
                image.fill((0,0,0) + (0,) , None, PG.BLEND_RGBA_ADD)

            screen.blit(image, Car.get_center_pos(self.positions[i],w,h))

    def update(self):
        self.life_counters += self.alive_list
        self.alive_list[self.life_counters > 1000] = False

        self.best = np.argmax(self.distances)

        # CHECK FOR SPEED LIMIT
        self.speeds[self.speeds < self.MIN_SPEED] = self.MIN_SPEED 

        # MOVE
        dx = (self.speeds * np.cos(np.radians(self.rotations)))
        dy = (self.speeds * np.sin(np.radians(self.rotations)))

        self.distances += np.sqrt(dx**2 + dy**2)

        self.positions += np.c_[dx,dy]

    def reset(self, i=None):
        if i is not None:
            raise NotImplementedError

        self.positions[:] = self.START_POSITION
        self.rotations[:] = self.START_ROTATION
        self.speeds[:] = self.START_SPEED

