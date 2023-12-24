#!/usr/bin/env python

from __future__ import annotations

import numpy as np
from src import Boundary

class World:
    def __init__(self, map : np.ndarray, checkpoints : list[Boundary.Checkpoint], start_pos : tuple[int,int], start_rot : float):
        self.map = map
        self.checkpoints = checkpoints
        self.start_pos = start_pos
        self.start_rot = start_rot
