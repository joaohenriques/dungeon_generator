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
    def pos_in_radius(pos, radius, radius_exclude=0):
        x,y = pos
        for r in range(radius_exclude+1, radius + 1):
            # corners first
            yield (x-r, y-r)
            yield (x+r, y-r)
            yield (x+r, y+r)
            yield (x-r, y+r)
            for d in range(1, r * 2):
                yield (x-r+d, y-r)
                yield (x+r, y-r+d)
                yield (x+r-d, y+r)
                yield (x-r, y+r-d)

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
        self.width = width
        self.height = height

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

    def batch_set(self, values):
        for (x, y), val in values:
            try:
                if x < 0 or y < 0:
                    raise IndexError
                self._map[y][x] = val
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


class GridMapLog(GridMap):
    def __init__(self, height, width):
        super(GridMapLog, self).__init__(height, width)
        self._history = []

    @property
    def history(self):
        return self._history

    def set(self, pos, val):
        self._history.append(('set', (pos, val)))
        super(GridMapLog, self).set(pos, val)

    def batch_set(self, values):
        self._history.append(('batch_set', values))
        super(GridMapLog, self).batch_set(values)