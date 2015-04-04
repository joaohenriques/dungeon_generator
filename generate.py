__author__ = 'jpsh'

from common.maps import SquareMap
from generators.cellular_automata import *


def main():

    cave = SquareMap(40, 77)
    creator = RandomizeCave(.40)
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