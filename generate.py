__author__ = 'jpsh'

from renderers.text import TextRenderer
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

if __name__ == '__main__':
    main()