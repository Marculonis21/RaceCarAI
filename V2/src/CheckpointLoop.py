from __future__ import annotations

import pygame as PG

from src import Boundary
from src import RayCaster
from src import Colors

import sys
import numpy as np

def checkpoint_loop(screen : PG.Surface, clock : PG.time.Clock, boundary_map : np.ndarray) -> tuple[np.ndarray, list[Boundary.Checkpoint], tuple[int,int], int]:
    assert boundary_map is not None, "Boundary loop should be run first"

    def set_start(p1,p2):
        checkpoints.append(Boundary.Checkpoint(screen, Colors.START_COLOR, p1, p2))

        start_pos = ((p1[0] + p2[0])//2, (p1[1]+p2[1])//2)
        
        start_rotation = 0
        while True:
            screen.blit(surface, (0,0))
            for c in checkpoints:
                c.draw()

            m_pos = PG.mouse.get_pos()
            for event in PG.event.get():
                if event.type == PG.QUIT:
                    sys.exit(0)

                if event.type == PG.MOUSEBUTTONDOWN and event.button == 1: 
                    return start_rotation

            dx = start_pos[0] - m_pos[0]
            dy = start_pos[1] - m_pos[1]
            rads = np.arctan2(-dy,dx)
            rads %= 2*np.pi
            degs = np.degrees(rads) + 180

            start_rotation = degs

            X_1 = m_pos[0] + (np.cos(np.radians(degs + 225)) * 20)
            Y_1 = m_pos[1] - (np.sin(np.radians(degs + 225)) * 20)
            X_2 = m_pos[0] + (np.cos(np.radians(degs + 135)) * 20)
            Y_2 = m_pos[1] - (np.sin(np.radians(degs + 135)) * 20)

            # start arrow drawing
            PG.draw.line(screen, (255,100,100), start_pos, PG.mouse.get_pos(), 3)
            PG.draw.line(screen, (255,100,100), PG.mouse.get_pos(), (X_1,Y_1), 3)
            PG.draw.line(screen, (255,100,100), PG.mouse.get_pos(), (X_2,Y_2), 3)

            PG.display.flip()
            clock.tick(60)

    def set_checkpoint(p1,p2):
        color = (Colors.CHECKPOINT_COLOR[0],
                 Colors.CHECKPOINT_COLOR[1],
                 Colors.CHECKPOINT_COLOR[2] - len(checkpoints)-1)

        checkpoints.append(Boundary.Checkpoint(screen, color, p1, p2))

    surface = PG.surfarray.make_surface(boundary_map)
    ray_caster = RayCaster.RayCaster(boundary_map, Colors.WALL_COLOR, 200)
    ray_caster.visible = True

    checkpoints : list[Boundary.Checkpoint] = []
    start_position = (0,0)
    start_rotation = 0

    while True:
        screen.blit(surface, (0,0))
        for c in checkpoints:
            c.draw()

        m_pos = PG.mouse.get_pos()

        ## DEBUG RAYCASTER TEST
        # step = 2
        # angles = np.arange(360//step) * step
        # hit, length, hit_pos = ray_caster.cast(m_pos, angles, screen, 2)

        for event in PG.event.get():
            if event.type == PG.QUIT:
                sys.exit(0)

            if event.type == PG.MOUSEBUTTONDOWN and event.button == 1: 

                # get all rays in circle
                hit_rays = []
                step = 2
                angles = np.arange(360//step) * step
                hit, length, hit_pos = ray_caster.cast(m_pos, angles, screen, 1)

                # from hits cast 180deg another
                end_points = []
                end_point_lengths = []
                for p, angle in zip(hit_pos[hit], angles[hit]):
                    p = np.array([p])
                    angle = np.array([angle])

                    _hit, _length, other_hit = ray_caster.cast(p,angle+180,screen,2)
                    if _hit and _length > 5:
                        end_point_lengths.append(float(_length))
                        end_points.append((p[0], other_hit[0]))

                # make checkpoint between shortest dists
                if len(end_points) > 0:
                    p1, p2 = end_points[np.argmin(end_point_lengths)]

                    if len(checkpoints) == 0:
                        start_rotation = set_start(p1,p2)
                    else:
                        set_checkpoint(p1,p2)

            if event.type == PG.KEYUP:
                if event.key == PG.K_RETURN:
                    return PG.surfarray.array3d(screen), checkpoints, checkpoints[0].pos, start_rotation

        PG.display.flip()
        clock.tick(60)
