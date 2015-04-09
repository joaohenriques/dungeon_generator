__author__ = 'jpsh'

import os
from renderers.text import TextRenderer
from renderers.gui_pygame import PygameRenderer
from generators.cellular_automata import *
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
             # Clear the console
            self._clear_console()
            out_str = self.renderer.render(play_cave)


def main():

    cave = GridMap(20, 40)
    creator = RandomizeCave(.35)
    smooth = SmoothCave()
    closerooms = CloseRooms(area=3)
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
    closerooms = CloseRooms(area=3)
    flood = HardenWallsCave()
    linkroom = LinkRooms()

    command_queue = [creator, smooth, closerooms, linkroom, flood]

    for command in command_queue:
        cave = command.execute(cave)

    renderer = TextRenderer()
    print(renderer.render(cave))

import pygame
from pygame.color import Color
import random

def main_pygame():

    width = 100
    height = 100
    block_size = 5
    wall_prob = .4

    cave = GridMap(height, width)
    creator = RandomizeCave(wall_prob)
    smooth = SmoothCave()
    close_rooms = CloseRooms(area=3)
    flood = HardenWallsCave()
    link_rooms = LinkRooms()

    command_queue = [creator, smooth, smooth, link_rooms, close_rooms, flood]

    for command in command_queue:
        cave = command.execute(cave)

    pygame.init()
    screen = pygame.display.set_mode((width*block_size, height*block_size))
    clock = pygame.time.Clock()
    screen.fill(Color('black'))

    play_cave = GridMap(cave.height, cave.width)
    history = cave.history

    renderer = PygameRenderer(block_size)

    done = False
    while not done:
        for event in pygame.event.get(): # User did something
            if event.type == pygame.QUIT: # If user clicked close
                done = True

        # update
        if len(history) > 0:
            pos, value = history.pop(0)
            play_cave.set(pos, value)

        #render
        #for pos, value in play_cave.items():
            pos_out = (pos[0]*block_size, pos[1]*block_size)
            screen.blit(renderer.render_cell(value), pos_out, None)

        pygame.display.flip()
        clock.tick()


if __name__ == '__main__':
    main_pygame()
    #main_no_animation()
