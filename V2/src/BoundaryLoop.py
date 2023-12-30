from __future__ import annotations

import pygame as PG
import pygame.freetype

from src import Boundary
from src import Colors

import sys

import numpy as np

def boundary_loop(screen : PG.Surface, clock : PG.time.Clock) -> np.ndarray:
    pygame.freetype.init()
    font = pygame.freetype.SysFont("roboto", 20)

    text = ["LMB - draw track boundary",
            "RMB - erase track boundary",
            "C - clear all",
            "MOUSEWHEEL - change brush size",
            "ENTER - confirm track shape and continue"
            ]

    brush_radius = 20

    boundaries : list[Boundary.CircleBoundary] = []

    while True:
        screen.fill(Colors.BG_COLOR)
        for b in boundaries:
            b.draw(screen)

        m_pos = PG.mouse.get_pos()
        for event in PG.event.get():
            if event.type == PG.QUIT:
                sys.exit(0)

            if event.type == PG.KEYUP:
                if event.key == PG.K_RETURN:
                    return PG.surfarray.array3d(screen)

                if event.key == PG.K_c:
                    boundaries = []

            if event.type == PG.MOUSEBUTTONDOWN:
                if event.button == 4:
                    if brush_radius < 100:
                        brush_radius += 1
                elif event.button == 5:
                    if brush_radius > 5:
                        brush_radius -= 1

            # drawing
            if PG.mouse.get_pressed()[0] or PG.mouse.get_pressed()[2]:
                boundaries.append(Boundary.CircleBoundary(m_pos,
                                                          brush_radius,
                                                          Colors.WALL_COLOR if PG.mouse.get_pressed()[0] else Colors.BG_COLOR))

        for i, t in enumerate(text):
            text_surf = font.render(t, PG.Color("White"))
            screen.blit(text_surf[0], (10,10+i*23))

        PG.draw.circle(screen, PG.Color("white"), m_pos, brush_radius, 1)

        PG.display.flip()
        clock.tick(60)
