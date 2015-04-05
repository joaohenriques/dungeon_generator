from __future__ import print_function

__author__ = 'jpsh'

from maps.grid import GridMap
from timeit import timeit

grid = GridMap(20, 20)


def keys():
    for pos in grid.keys():
        pass

def values():
    for val in grid.values():
        pass

def items():
    for pos, val in grid.items():
        pass

def raw():
    lst = []
    for y in range(0, 20):
        for x in range(0, 20):
            pass
            lst.append((x, y))

print("keys={}".format(timeit(keys, number=100)))
print("values={}".format(timeit(values, number=100)))
print("items={}".format(timeit(items, number=100)))
print("raw={}".format(timeit(raw, number=100)))