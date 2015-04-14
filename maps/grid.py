__author__ = 'jpsh'

from maps import Tile


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
    def bounding_box(cells):
        lst = list(cells)
        x1, y1 = lst[0]
        x2, y2 = lst[0]

        for x, y in lst[1:]:
            x1 = min(x1, x)
            y1 = min(y1, y)
            x2 = max(x2, x)
            y2 = max(y2, y)

        return x1, y1, x2, y2


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

    def keys(self, bb=None, tileset=None):
        if not bb:
            bb = (0, 0, self.width, self.height)
        return ((x, y) for y in range(bb[1], bb[3]) for x in range(bb[0], bb[2])
                if not tileset or self._map[y][x] in tileset)

    def values(self, bb=None):
        if not bb:
            bb = (0, 0, self.width, self.height)
        return (self._map[y][x] for y in range(bb[1], bb[3]) for x in range(bb[0], bb[2]))

    def items(self, bb=None, tileset=None):
        if not bb:
            bb = (0, 0, self.width, self.height)
        return (((x, y), self._map[y][x]) for y in range(bb[1], bb[3]) for x in range(bb[0], bb[2])
                if not tileset or self._map[y][x] in tileset)
