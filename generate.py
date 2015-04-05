__author__ = 'jpsh'

import sys
import os
from renderers.text import TextRenderer
from generators.cellular_automata import *
from maps import Tile
from maps.grid import GridMap
import logging

logger = logging.getLogger('dungeon_generation')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('dungeon_generation.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(name)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


class Animator(object):

    def __init__(self, cave, renderer):
        self.cave = cave
        self.renderer = renderer

    @staticmethod
    def _clear_console():
        if os.name == 'posix':
            os.system('clear')
        else:
            os.system('CLS')

    def animate(self):
        play_cave = GridMap(self.cave.height, self.cave.width)

        for pos, val in self.cave.history:
            play_cave.set(pos, val)
            out_str = self.renderer.render(play_cave)

            # Clear the console
            self._clear_console()
            # Write the current frame on stdout and sleep
            sys.stdout.write(out_str)
            sys.stdout.flush()


def main():

    cave = GridMap(20, 40)
    creator = RandomizeCave(.35)
    smooth = SmoothCave()
    closerooms = CloseOneSquareRooms()
    flood = HardenWallsCave()
    linkroom = LinkRooms()

    command_queue = [creator, smooth, closerooms, linkroom, flood]

    for command in command_queue:
        cave = command.execute(cave)

    renderer = TextRenderer()
    animator = Animator(cave, renderer)
    animator.animate()


def main_no_animation():

    cave = GridMap(40, 77)
    creator = RandomizeCave(.35)
    smooth = SmoothCave()
    closerooms = CloseOneSquareRooms()
    flood = HardenWallsCave()
    linkroom = LinkRooms()

    command_queue = [creator, smooth, closerooms, linkroom, flood]

    for command in command_queue:
        cave = command.execute(cave)

    renderer = TextRenderer()
    print(renderer.render(cave))

import pygame
from pygame import Surface
from pygame.color import Color

def main_pygame():

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    screen.fill(Color('black'))

    cave = GridMap(20, 40)
    creator = RandomizeCave(.35)
    smooth = SmoothCave()
    closerooms = CloseOneSquareRooms()
    flood = HardenWallsCave()
    linkroom = LinkRooms()

    command_queue = [creator, smooth, closerooms, linkroom, flood]

    for command in command_queue:
        cave = command.execute(cave)

    play_cave = GridMap(cave.height, cave.width)
    history = cave.history

    size = 10
    earth = Surface((size, size))
    earth.fill(Color('brown'))
    wall = Surface((size, size))
    wall.fill(Color('grey'))
    floor = Surface((size, size))
    floor.fill(Color('white'))
    unknown = Surface((size, size))
    unknown.fill(Color('yellow'))

    done = False
    while not done:
        for event in pygame.event.get(): # User did something
            if event.type == pygame.QUIT: # If user clicked close
                done = True

        # update
        if len(history) > 0:
            pos, val = history.pop(0)
            play_cave.set(pos, val)

        #render
        for pos, value in play_cave.items():
            pos = (pos[0]*size, pos[1]*size)
            if value == Tile.EARTH:
                screen.blit(earth, pos, None)
            if value == Tile.WALL:
                screen.blit(wall, pos, None)
            if value == Tile.FLOOR:
                screen.blit(floor, pos, None)
            if value == Tile.UNKNOWN:
                screen.blit(unknown, pos, None)

        pygame.display.flip()
        elapsed = clock.tick()
        logger.info("render time={0:.3f}ms".format(elapsed))

if __name__ == '__main__':
    main_pygame()