__author__ = 'jpsh'

from renderers import MapRenderer
from maps import Tile
import sys

class TextRenderer(MapRenderer):

    def render(self, cave, fp=sys.stdout):
        str_buffer = []
        width = cave.width
        str_buffer.append("#" * (width+2))
        str_buffer.append("\n")
        str_buffer.append("#")
        col = 0
        for val in cave.values():
            col += 1
            str_buffer.append(self.render_cell(val))

            if col % width == 0:
                col = 0
                str_buffer.append("#")
                str_buffer.append("\n")
                str_buffer.append("#")

        str_buffer.append("#" * (width+1))
        fp.write("".join(str_buffer))
        fp.flush()


    def render_cell(self, val):
        if val == Tile.WALL:
            return '#'
        elif val == Tile.FLOOR:
            return ' '
        elif val == Tile.EARTH:
            return '+'
        else:
            return '?'