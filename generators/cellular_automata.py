from __future__ import print_function

__author__ = 'jpsh'

import time
from random import random, choice
from abc import ABCMeta, abstractmethod
from maps import Tile
from maps.grid import GridTools

import logging
LOGGING_PREFIX = 'dungeon_generation.cellular_automata.'


class CaveGenerationCommand(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def _execute(self, cave):
        pass

    def execute(self, cave):
        self._log().debug("beginning of execution")
        try:
            start = time.time()
            cave = self._execute(cave)
            elapsed = time.time() - start
            self._log().info("execution time={0:.3f}s".format(elapsed))
        finally:
            self._log().debug("end of execution")
        return cave

    def _log(self):
        return logging.getLogger(LOGGING_PREFIX + self.__class__.__name__)


class RandomizeCave(CaveGenerationCommand):

    def __init__(self, prob):
        self.prob = prob
        
    def _gen_square(self):
        if random() >= self.prob:
            return Tile.EARTH
        else:
            return Tile.FLOOR
    
    def _execute(self, cave):
        for pos in cave.keys():
            cave.set(pos, self._gen_square())
        return cave


class SmoothCave(CaveGenerationCommand):

    def _execute(self, cave):
        for pos in cave.keys():
            walls = 0
            if cave.get(GridTools.nw(pos)) != Tile.FLOOR:
                walls += 1
            if cave.get(GridTools.n(pos)) != Tile.FLOOR:
                walls += 1
            if cave.get(GridTools.ne(pos)) != Tile.FLOOR:
                walls += 1

            if cave.get(GridTools.w(pos)) != Tile.FLOOR:
                walls += 1
            if cave.get(GridTools.e(pos)) != Tile.FLOOR:
                walls += 1

            if cave.get(GridTools.sw(pos)) != Tile.FLOOR:
                walls += 1
            if cave.get(GridTools.s(pos)) != Tile.FLOOR:
                walls += 1
            if cave.get(GridTools.se(pos)) != Tile.FLOOR:
                walls += 1

            if walls > 5:
                cave.set(pos, Tile.EARTH)
            elif walls < 4:
                cave.set(pos, Tile.FLOOR)
                       
        return cave


class HardenWallsCave(CaveGenerationCommand):

    def _execute(self, cave):
        flooded = set()
        for pos in cave.keys(filter_expr=lambda x: x == Tile.FLOOR):
            if pos not in flooded:
                cave = self._flood_tile(cave, pos, flooded)
        return cave

    @staticmethod
    def _flood_tile(cave, pos, flooded):
        stack = [pos]

        while len(stack) > 0:
            pos = stack.pop()

            if pos in flooded:
                continue

            tile = cave.get(pos)
            if tile == Tile.FLOOR:
                flooded.add(pos)
                stack.append(GridTools.n(pos))
                stack.append(GridTools.ne(pos))
                stack.append(GridTools.e(pos))
                stack.append(GridTools.se(pos))
                stack.append(GridTools.s(pos))
                stack.append(GridTools.sw(pos))
                stack.append(GridTools.w(pos))
                stack.append(GridTools.nw(pos))

            elif tile == Tile.EARTH:
                cave.set(pos, Tile.WALL)

        return cave


class CloseRooms(CaveGenerationCommand):

    def __init__(self, area=1):
        self.area = area
        
    def _execute(self, cave):
        flooded = set()
        for pos in cave.keys(filter_expr=lambda x: x == Tile.FLOOR):
            if pos not in flooded:
                room = self._flood_room(cave, pos)
                if len(room) <= self.area:
                    for cell in room:
                        cave.set(cell, Tile.EARTH)
                flooded.update(room)
        return cave
    
    @staticmethod
    def _flood_room(cave, pos):
        flooded = set()
        stack = [pos]

        while len(stack) > 0:
            pos = stack.pop()

            if pos in flooded:
                continue

            tile = cave.get(pos)
            if tile == Tile.FLOOR:
                flooded.add(pos)
                stack.append(GridTools.n(pos))
                stack.append(GridTools.e(pos))
                stack.append(GridTools.s(pos))
                stack.append(GridTools.w(pos))

        return flooded
    
    
class LinkRooms(CaveGenerationCommand):

    def _execute(self, cave):
        rooms = self._find_rooms(cave)

        while len(rooms) > 1:
            paths = []
            done = False
            for i in range(0, len(rooms)):
                if done:
                    break
                for j in range(i+1, len(rooms)):
                    room_a = rooms[i]
                    room_b = rooms[j]
                    path = self._calculate_distance(room_a, room_b)
                    paths.append((path, (i, j)))
                    if path[0] < 4:
                        done = True
                        break

            paths.sort()
            shortest, (a, b) = paths[0]

            (pos_s, pos_t) = choice(shortest[1])
            corridor = self.dig(pos_s, pos_t)
            rooms[a].update(corridor)
            rooms[a].update(rooms[b])
            del rooms[b]

            for pos in corridor:
                cave.set(pos, Tile.FLOOR)

        return cave

    @staticmethod
    def dig(start, end):
        xs, ys = start
        xt, yt = end
        dx = xt - xs
        dy = yt - ys

        corridor = [start,end]

        x, y = xs, ys
        while x != xt or y != yt:
            if x != xt and y == yt:
                x += dx/abs(dx)
            elif x == xt and y != yt:
                y += dy/abs(dy)
            else:
                if random() > 0.5:
                    x += dx/abs(dx)
                else:
                    y += dy/abs(dy)
            pos = (int(x), int(y))
            corridor.append(pos)

        return corridor

    @staticmethod
    def _calculate_distance(room_a, room_b):
        min_distance = 1000000000.0
        closest = []
        for pos_a in room_a:
            for pos_b in room_b:
                distance = GridTools.distance(pos_a, pos_b)
                if distance == min_distance:
                    closest.append((pos_a, pos_b))
                elif distance < min_distance:
                    min_distance = distance
                    closest = [(pos_a, pos_b)]

        return min_distance, closest

    def _find_rooms(self, cave):
        rooms = set()
        result = []

        for pos in cave.keys(filter_expr=lambda x: x == Tile.FLOOR):
            if pos not in rooms:
                room = self._flood_room(cave, pos)
                rooms.update(room)
                result.append(room)

        return result

    @staticmethod
    def _flood_room(cave, pos):
        room = set()
        stack = [pos]

        while len(stack) > 0:
            pos = stack.pop()

            if pos in room:
                continue

            tile = cave.get(pos)
            if tile == Tile.FLOOR:
                room.add(pos)
                stack.append(GridTools.n(pos))
                stack.append(GridTools.e(pos))
                stack.append(GridTools.s(pos))
                stack.append(GridTools.w(pos))

        return room


class MapRender(object):
    __metaclass__ = ABCMeta
        
    @abstractmethod
    def render(self, cave):
        pass
