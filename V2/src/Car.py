#!/usr/bin/env python3

from __future__ import annotations

import pygame as PG
import numpy as np

from src import Colors
from src import Boundary
from src import WorldData
from src import RayCaster

class Car:
    @staticmethod
    def get_center_pos(pos, image):
        return (int(pos[0] - image.get_width()/2), int(pos[1] - image.get_height()/2))

    @staticmethod
    def get_corner_points(pos, rots, image):
        ''' GET CORNER POSITIONS - COLLISION DETECTION '''
        car_height = image.get_height()
        car_width = image.get_width()

        up = np.c_[np.cos(np.radians(rots)), -np.sin(np.radians(rots))]
        up_ex = np.c_[up, np.zeros(up.shape[0])]
        right = np.cross(up_ex, np.array([0,0,-1]))[:,:2]

        NN = np.clip(pos + up*car_height + right*0, 0, 799)

        NE = np.clip(pos + (up*(car_height-5)) + (right*car_width/5),0,799)
        NW = np.clip(pos + (up*(car_height-5)) - (right*car_width/5),0,799)

        SE = np.clip(pos + (up*(-car_height+2)) + (right*car_width/5),0,799)
        SW = np.clip(pos + (up*(-car_height+2)) - (right*car_width/5),0,799)

        return up, right, NN.astype(int), NE.astype(int), NW.astype(int), SE.astype(int), SW.astype(int)

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
    def __init__(self, count, world_data : WorldData.World):
        self.__init_image()
        self.count = count

        self.positions = np.zeros([count,2])
        self.rotations = np.zeros([count])
        self.speeds = np.zeros([count])

        self.life_counters = np.zeros([count])
        self.distances = np.zeros([count])

        self.alive_list = np.ones([count])

        self.last_start_counter = np.zeros([count])

        self.world_data = world_data

        self.MIN_SPEED = 2.5
        self.START_SPEED = 3

        # per car - list of tuples <checkpoint_id, time> (staring at (0,0))
        self.checkpoint_rankings : list[list[tuple[int, float]]] = [[(0,0)] for _ in range(self.count)]

        self.ray_caster = RayCaster.RayCaster(self.world_data.map, Colors.WALL_COLOR, 200)

        # ready to use after init
        self.reset()
        
    def __init_image(self):
        image = PG.image.load("./data/carClipArt.jpg")
        size = 50

        w = image.get_rect().size[1]
        h = image.get_rect().size[0]
        r = w/h

        self.car_image = PG.transform.scale(image, (size,int(size*r)))
        
    def draw(self, screen, debug=False):
        for i in range(self.count):
            # image = self.car_image.copy()
            image = PG.transform.rotate(self.car_image, self.rotations[i])
            if self.alive_list[i]:
                if np.argmax(self.distances) == i and self.count > 1:
                    image.fill((255, 0, 0, 255), None, PG.BLEND_RGBA_MULT)
                    image.fill((100,0,0) + (0,) , None, PG.BLEND_RGBA_ADD)

            else:
                image.fill((50, 50, 50, 210), None, PG.BLEND_RGBA_MULT)
                image.fill((0,0,0) + (0,) , None, PG.BLEND_RGBA_ADD)

            screen.blit(image, Car.get_center_pos(self.positions[i], image))

            if debug:
                up, right, NN, NE, NW, SE, SW = Car.get_corner_points(self.positions[i], self.rotations[i], self.car_image) # using orig image

                PG.draw.line(screen, PG.Color(0,255,0), self.positions[i], self.positions[i]+20*up[0], 2)
                PG.draw.line(screen, PG.Color(255,0,0), self.positions[i], self.positions[i]+20*right[0], 2)

                PG.draw.circle(screen, PG.Color(255,0,0), NN[0], 2)
                PG.draw.circle(screen, PG.Color(255,0,0), NE[0], 2)
                PG.draw.circle(screen, PG.Color(255,0,0), NW[0], 2)
                PG.draw.circle(screen, PG.Color(255,0,0), SE[0], 2)
                PG.draw.circle(screen, PG.Color(255,0,0), SW[0], 2)

    def __collision_handling(self):
        # Collision detection
        _, _, NN, NE, NW, SE, SW = Car.get_corner_points(self.positions, self.rotations, self.car_image) # using orig image

        tests = np.c_[self.world_data.map[NN[:,0], NN[:,1]], 
                      self.world_data.map[NE[:,0], NE[:,1]],
                      self.world_data.map[NW[:,0], NW[:,1]],
                      self.world_data.map[SE[:,0], SE[:,1]],
                      self.world_data.map[SW[:,0], SW[:,1]]].reshape(self.count,5,3)

        wall_collision = np.sum((tests == np.array(Colors.WALL_COLOR)).reshape(self.count,-1),axis=1) == 0
        self.alive_list *= wall_collision

        for i, c in enumerate(self.world_data.checkpoints):
            c_collision = np.sum((tests == np.array(c.color)).reshape(self.count,-1), axis=1)

            for id in range(self.count):
                # hit at least one true and have one whole color right
                if c_collision[id] > 0 and c_collision[id] % 3 == 0:
                    if (self.checkpoint_rankings[id][-1][0] >= i-1) or \
                       (self.checkpoint_rankings[id][-1][0] == len(self.world_data.checkpoints)-1 and i == 0):
                        self.checkpoint_rankings[id].append((i, self.life_counters[id]))
                        if c.color == Colors.START_COLOR:
                            self.last_start_counter[id] = self.life_counters[id]

        # print(self.checkpoint_rankings)

    def update(self):
        self.life_counters += self.alive_list
        self.alive_list[self.life_counters > 1000] = False

        # CHECK FOR SPEED LIMIT
        self.speeds[self.speeds < self.MIN_SPEED] = self.MIN_SPEED 

        # MOVE
        dx = (self.speeds *  np.cos(np.radians(self.rotations)))
        dy = (self.speeds * -np.sin(np.radians(self.rotations)))
        delta = np.c_[dx,dy]

        self.distances += np.linalg.norm(delta, axis=1)*self.alive_list

        self.positions += delta*self.alive_list.reshape(-1,1)

        self.__collision_handling()

    def observation(self, screen=PG.Surface((0,0)), debug=False):
        self.ray_caster.visible = debug
        observation = np.zeros([self.count, 6])

        _,_,NN,_,_,_,_ = Car.get_corner_points(self.positions, self.rotations, self.car_image) # using orig image
        angles = np.array([-60 + 30*rot for rot in range(5)])

        for id in range(self.count):
            if not self.alive_list[id]: continue

            _,length,_ = self.ray_caster.cast(NN[id], -self.rotations[id] + angles, screen, 2)
            observation[id] = np.r_[length/self.ray_caster.max_length,0]
            
        observation[:, 5] = (self.life_counters-self.last_start_counter)/1000.0

        return observation

    def any_alive(self):
        return np.sum(self.alive_list) > 0

    def reset(self, i=None):
        if i is not None:
            raise NotImplementedError

        self.positions[:] = self.world_data.start_pos
        self.rotations[:] = self.world_data.start_rot
        self.speeds[:] = self.START_SPEED
        self.life_counters[:] = 0
        self.distances[:] = 0
        self.alive_list[:] = 1

        self.checkpoint_rankings  = [[(0,0)] for _ in range(self.count)]
        self.last_start_counter[:] = 0

    def input_controller(self, inputs : np.ndarray):
        assert len(inputs) == self.count, "Assign inputs for all cars at once"

        # power up|stable|down
        # steer left|front|right

        power_input, steer_input = inputs[:,0].astype(np.float64), inputs[:,1].astype(np.float64)
        
        p_change = np.logical_or(power_input > 0.25, power_input < -0.25)
        self.speeds += self.alive_list * p_change * 0.4*power_input

        s_change = np.logical_or(steer_input > 0.1, steer_input < -0.1)
        self.rotations += self.alive_list * s_change * 5.0*steer_input

    def input_player(self, i, input : tuple[bool, bool, bool, bool]):
        if not self.alive_list[i]: return

        if input[0]:
            self.speeds[i] += 0.5
        elif input[1]:
            self.speeds[i] -= 0.5

        if input[2]:
            self.rotations[i] += 1
        elif input[3]:
            self.rotations[i] -= 1

    def calc_fitness(self) -> np.ndarray:
        # HARD-CODED for now - up for change later
        DIST_VALUE, CHECK_VALUE, SPEED_VALUE = 0.75, 50.0, 100.0

        fitness = np.zeros([self.count])

        fitness += self.distances*DIST_VALUE

        most_checkpoints = -1
        for id in range(self.count):
            if len(self.checkpoint_rankings[id]) > most_checkpoints:
                most_checkpoints = len(self.checkpoint_rankings[id])

            fitness[id] += len(self.checkpoint_rankings[id])*CHECK_VALUE

        for i in range(1, most_checkpoints):
            car_ids = [id for id in range(self.count) if len(self.checkpoint_rankings[id]) > i]
            car_times = np.array([self.checkpoint_rankings[id][i][1] for id in car_ids])

            argsort_times = np.argsort(car_times)

            for rank, index in enumerate(argsort_times):
                id = car_ids[index]
                fitness[id] += SPEED_VALUE - rank*(SPEED_VALUE/len(car_ids))

        return fitness
    
    def calc_fitness_immediate(self) -> np.ndarray:
        DIST_VALUE, CHECK_VALUE, SPEED_VALUE = 1, 20.0, 100.0

        fitness = np.zeros([self.count])
        fitness += self.distances*DIST_VALUE

        for id in range(self.count):
            fitness[id] += len(self.checkpoint_rankings[id])*CHECK_VALUE

        fitness += -500*np.logical_not(self.alive_list)

        return fitness
