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
    # ray_caster.visible = True

    checkpoints : list[Boundary.Checkpoint] = []
    start_position = (0,0)
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
                step = 4

                hit_rays = []
                for a in range(360//step):
                    hit, length, hit_pos = ray_caster.cast(m_pos, a*step, screen, 2)
                    if not hit: continue

                    hit_rays.append((length, hit_pos, a*step))

                hit_rays = sorted(hit_rays, key=lambda x: x[0])
                end_points = []

                for hr in hit_rays:
                    p1 = hr[1]
                    p1_a = hr[2]

                    hit, length, hit_pos = ray_caster.cast(p1,p1_a+180,screen,2)
                    if hit and length > 5:
                        end_points.append((p1,hit_pos))

                end_points = sorted(end_points, key=lambda x: (x[0][0]-x[1][0])**2 + (x[0][1]-x[1][1])**2)

                if len(end_points) > 0:
                    p1,p2 = end_points[0]

                    if len(checkpoints) == 0:
                        start_rotation = set_start(p1,p2)
                    else:
                        set_checkpoint(p1,p2)

            if event.type == PG.KEYUP:
                if event.key == PG.K_RETURN:
                    return PG.surfarray.array3d(screen), checkpoints, checkpoints[0].pos, start_rotation

        PG.display.flip()
        clock.tick(60)
