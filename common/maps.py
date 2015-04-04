__author__ = 'jpsh'

from collections import namedtuple
from common import Tile


Point = namedtuple('Point', ['x', 'y'])


class Square(Point):

    def __init__(self, x, y, **kwargs):
        super(Point, self).__init__(x, y, **kwargs)

    @property
    def n(self):
        return Square(self.x, self.y-1)

    @property
    def ne(self):
        return Square(self.x+1, self.y-1)

    @property
    def e(self):
        return Square(self.x+1, self.y)

    @property
    def se(self):
        return Square(self.x+1, self.y+1)

    @property
    def s(self):
        return Square(self.x, self.y+1)

    @property
    def sw(self):
        return Square(self.x-1, self.y+1)

    @property
    def w(self):
        return Square(self.x-1, self.y)

    @property
    def nw(self):
        return Square(self.x-1, self.y-1)

    def __repr__(self):
        return "Position(x={}, y={})".format(self.x, self.y)

    def __str__(self):
        return "({}, {})".format(self.x, self.y)


class SquareMap(object):

    def __init__(self, height, width):
        self._map = [[Tile.UNKNOWN for _ in range(0, width)] for _ in range(0, height)]

    @property
    def width(self):
        return len(self._map[0])

    @property
    def height(self):
        return len(self._map)

    def get(self, pos):
        x, y = pos
        try:
            if x < 0 or y < 0:
                raise IndexError
            return self._map[y][x]
        except IndexError:
            # TODO log
            return Tile.UNKNOWN

    def set(self, pos, val):
        x, y = pos
        try:
            if x < 0 or y < 0:
                raise IndexError
            self._map[y][x] = val
        except IndexError:
            # TODO log
            pass

    def keys(self, start_pos=None, end_pos=None, filter_expr=None):
        if not start_pos:
            start_pos = (0, 0)
        if not end_pos:
            end_pos = (self.width, self.height)
        if not filter_expr:
            filter_expr = lambda _: True
        return (Square(x, y) for y in range(start_pos[1], end_pos[1]) for x in range(start_pos[0], end_pos[0])
                if filter_expr(self._map[y][x]))

    def values(self, start_pos=None, end_pos=None):
        if not start_pos:
            start_pos = (0, 0)
        if not end_pos:
            end_pos = (self.width, self.height)
        return (self._map[y][x] for y in range(start_pos[1], end_pos[1]) for x in range(start_pos[0], end_pos[0]))

    def items(self, start_pos=None, end_pos=None, filter_expr=None):
        if not start_pos:
            start_pos = (0, 0)
        if not end_pos:
            end_pos = (self.width, self.height)
        if not filter_expr:
            filter_expr = lambda _: True
        return ((Square(x, y), self._map[y][x]) for y
                in range(start_pos[1], end_pos[1]) for x in range(start_pos[0], end_pos[0])
                if filter_expr(self._map[y][x]))
