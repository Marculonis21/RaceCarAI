#!/usr/bin/env python

from __future__ import annotations

import numpy as np
from src import Boundary

import pickle
import pygame as PG
import os

PATH = "data/user_data/"

class World:
    def __init__(self, map : np.ndarray, checkpoints : list[Boundary.Checkpoint], start_pos : tuple[int,int], start_rot : float):
        self.map = map
        self.checkpoints = checkpoints
        self.start_pos = start_pos
        self.start_rot = start_rot

    @staticmethod
    def save(data : World, name):
        if not os.path.isdir(PATH): os.mkdir(PATH)

        surface = PG.surfarray.make_surface(data.map)
        save_filename = f"{name}.save"
        map_filename = f"p_{name}.jpg"
        PG.image.save(surface, PATH + map_filename)

        save_dict = {
            "map_file" : map_filename,
            "checkpoints" : data.checkpoints,
            "start_pos" : data.start_pos,
            "start_rot" : data.start_rot,
        }

        with open(PATH + save_filename, 'wb') as f:
            pickle.dump(save_dict, f)

    @staticmethod
    def load(name) -> World | None:
        if not os.path.isfile(PATH + name + ".save"):
            print(f"Save file {name}.save not found") 
            return None

        data = None

        save_filename = f"{name}.save"
        with open(PATH + save_filename, 'rb') as f:
            data = pickle.load(f)

        assert data is not None, "File not loaded"

        if not os.path.isfile(PATH + data["map_file"]):
            print(f"Picture " + data["map_file"] + " not found") 

        surface = PG.image.load(PATH + data["map_file"])
        return World(PG.surfarray.array3d(surface), data["checkpoints"], data["start_pos"], data["start_rot"])
