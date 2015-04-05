__author__ = 'jpsh'

from renderers import MapRenderer
from maps import Tile


class TextRenderer(MapRenderer):

    def render(self, cave):
        str_buffer = []
        width = cave.width
        str_buffer.append("#" * (width+2))
        str_buffer.append("\n")
        str_buffer.append("#")
        col = 0
        for val in cave.values():
            col += 1
            if val == Tile.WALL:
                str_buffer.append('#')
            elif val == Tile.FLOOR:
                str_buffer.append(' ')
            elif val == Tile.EARTH:
                str_buffer.append('+')
            else:
                str_buffer.append('?')

            if col % width == 0:
                col = 0
                str_buffer.append("#")
                str_buffer.append("\n")
                str_buffer.append("#")
        str_buffer.append("#" * (width+1))

        return "".join(str_buffer)