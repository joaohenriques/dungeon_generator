__author__ = 'jpsh'

from common.maps import SquareMap
from generators.cellular_automata import *

import logging

logger = logging.getLogger('dungeon_generation')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('dungeon_generation.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(name)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


def main():

    cave = SquareMap(40, 77)
    creator = RandomizeCave(.35)
    smooth = SmoothCave()
    closerooms = CloseOneSquareRooms()
    flood = HardenWallsCave()
    linkroom = LinkRooms()

    renderer = TextRenderer()
    animator = Animator(renderer, cave)

    animator.add_command(creator)
    animator.add_command(smooth)
    animator.add_command(closerooms)
    animator.add_command(linkroom)
    animator.add_command(flood)

    animator.animate(delay=0.1)

if __name__ == '__main__':
    main()