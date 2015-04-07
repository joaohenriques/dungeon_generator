__author__ = 'jpsh'

from maps import Tile
from math import hypot


class GridTools(object):
    @staticmethod
    def n(pos):
        return pos[0], pos[1]-1

    @staticmethod
    def ne(pos):
        return pos[0]+1, pos[1]-1

    @staticmethod
    def e(pos):
        return pos[0]+1, pos[1]

    @staticmethod
    def se(pos):
        return pos[0]+1, pos[1]+1

    @staticmethod
    def s(pos):
        return pos[0], pos[1]+1

    @staticmethod
    def sw(pos):
        return pos[0]-1, pos[1]+1

    @staticmethod
    def w(pos):
        return pos[0]-1, pos[1]

    @staticmethod
    def nw(pos):
        return pos[0]-1, pos[1]-1

    @staticmethod
    def distance(pos, other):
        return hypot(pos[0]-other[0], pos[1]-other[1])


class GridMap(object):

    def __init__(self, height, width):
        self._map = [[Tile.UNKNOWN for _ in range(0, width)] for _ in range(0, height)]
        self._history = []

    @property
    def width(self):
        return len(self._map[0])

    @property
    def height(self):
        return len(self._map)

    @property
    def history(self):
        return self._history

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
            self._history.append((pos, val))
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
        return ((x, y) for y in range(start_pos[1], end_pos[1]) for x in range(start_pos[0], end_pos[0])
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
        return (((x, y), self._map[y][x]) for y
                in range(start_pos[1], end_pos[1]) for x in range(start_pos[0], end_pos[0])
                if filter_expr(self._map[y][x]))

class GridMapDict(object):
    def __init__(self, height, width):
        self._map = {}
        self._width = height
        self._height = height
        self._history = []
        for y in xrange(0, height):
            for x in xrange(0, width):
                self._map[(x, y)] = Tile.UNKNOWN

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def history(self):
        return self._history

    def get(self, pos):
        try:
            return self._map[pos]
        except KeyError:
            # TODO log
            return Tile.UNKNOWN

    def set(self, pos, tile):
        try:
            self._map[pos] = tile
            self._history.append((pos, tile))
        except KeyError:
            # TODO log
            pass

    def keys(self, filter_expr=None):

        if not filter_expr:
            filter_expr = lambda _: True

        return (pos for pos, val in self._map.items() if filter_expr(val))

    def values(self):
        return self._map.values()

    def items(self, filter_expr=None):

        if not filter_expr:
            filter_expr = lambda _: True

        return ((pos, val) for pos, val in self._map.items() if filter_expr(val))