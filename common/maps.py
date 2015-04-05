__author__ = 'jpsh'

from collections import namedtuple
from common import Tile
from math import sqrt

Point = namedtuple('Point', ['x', 'y'])


class GridPosition(Point):

    def __init__(self, x, y, **kwargs):
        super(Point, self).__init__(x, y, **kwargs)

    @property
    def n(self):
        return GridPosition(self.x, self.y-1)

    @property
    def ne(self):
        return GridPosition(self.x+1, self.y-1)

    @property
    def e(self):
        return GridPosition(self.x+1, self.y)

    @property
    def se(self):
        return GridPosition(self.x+1, self.y+1)

    @property
    def s(self):
        return GridPosition(self.x, self.y+1)

    @property
    def sw(self):
        return GridPosition(self.x-1, self.y+1)

    @property
    def w(self):
        return GridPosition(self.x-1, self.y)

    @property
    def nw(self):
        return GridPosition(self.x-1, self.y-1)

    def distance(self, other):
        return sqrt(pow(abs(self.x-other.x), 2) + pow(abs(self.y-other.y), 2))

    def __repr__(self):
        return "{}(x={}, y={})".format(self.__class__.__name__, self.x, self.y)

    def __str__(self):
        return "({}, {})".format(self.x, self.y)


class GridMap(object):

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
        return (GridPosition(x, y) for y in range(start_pos[1], end_pos[1]) for x in range(start_pos[0], end_pos[0])
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
        return ((GridPosition(x, y), self._map[y][x]) for y
                in range(start_pos[1], end_pos[1]) for x in range(start_pos[0], end_pos[0])
                if filter_expr(self._map[y][x]))
