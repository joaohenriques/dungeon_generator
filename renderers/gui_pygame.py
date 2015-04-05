__author__ = 'jpsh'

from renderers import MapRenderer
from maps import Tile
from pygame import Surface
from pygame.color import Color


class PygameRenderer(MapRenderer):

    def __init__(self, block_size):
        self.block_size = block_size
        self._earth = Surface((block_size, block_size))
        self._earth.fill(Color('brown'))
        self._wall = Surface((block_size, block_size))
        self._wall .fill(Color('grey'))
        self._floor = Surface((block_size, block_size))
        self._floor.fill(Color('white'))
        self._unknown = Surface((block_size, block_size))
        self._unknown.fill(Color('yellow'))

    def render(self, cave, out=None):
        if not out:
            return

        for pos, value in cave.items():
            pos_out = (pos[0]*self.block_size, pos[1]*self.block_size)
            out.blit(self.render_cell(value), pos_out, None)

    def render_cell(self, val):
        if val == Tile.WALL:
            return self._wall
        elif val == Tile.FLOOR:
            return self._floor
        elif val == Tile.EARTH:
            return self._earth
        else:
            return self._unknown