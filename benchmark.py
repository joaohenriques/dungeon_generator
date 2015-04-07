from __future__ import print_function

__author__ = 'jpsh'

from maps.grid import GridMap, GridMapDict
from generators.cellular_automata import *
from timeit import timeit
import random

def keys(grid):
    for pos in grid.keys():
        pass

def values(grid):
    for val in grid.values():
        pass

def items(grid):
    for pos, val in grid.items():
        pass

def raw(grid):
    lst = []
    for y in range(0, 20):
        for x in range(0, 20):
            pass
            lst.append((x, y))

def keys_filter(grid):
    for pos in grid.keys(filter_expr=lambda x: x == Tile.FLOOR):
        pass

def items_filter(grid):
    for pos, val in grid.items(filter_expr=lambda x: x == Tile.FLOOR):
        pass

def generate_map(cave):
    random.seed(0)
    creator = RandomizeCave(.34)
    smooth = SmoothCave()
    closerooms = CloseRooms(area=3)
    flood = HardenWallsCave()
    linkroom = LinkRooms()

    command_queue = [creator, smooth, closerooms, linkroom, flood]

    for command in command_queue:
        cave = command.execute(cave)

print("GridMap")
grid = GridMap(40, 40)
print("keys={}".format(timeit(lambda:keys(grid), number=100)))
print("keys_filter={}".format(timeit(lambda:keys_filter(grid), number=100)))
print("values={}".format(timeit(lambda:values(grid), number=100)))
print("items={}".format(timeit(lambda:items(grid), number=100)))
print("items_filter={}".format(timeit(lambda:items_filter(grid), number=100)))
print("raw={}".format(timeit(lambda:raw(grid), number=100)))
print("map={}".format(timeit(lambda:generate_map(grid), number=2)))

print("GridMapDict")
grid = GridMapDict(40, 40)
print("keys={}".format(timeit(lambda:keys(grid), number=100)))
print("keys_filter={}".format(timeit(lambda:keys_filter(grid), number=100)))
print("values={}".format(timeit(lambda:values(grid), number=100)))
print("items={}".format(timeit(lambda:items(grid), number=100)))
print("items_filter={}".format(timeit(lambda:items_filter(grid), number=100)))
print("raw={}".format(timeit(lambda:raw(grid), number=100)))
print("map={}".format(timeit(lambda:generate_map(grid), number=2)))
