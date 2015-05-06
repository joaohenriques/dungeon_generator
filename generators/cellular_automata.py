from __future__ import print_function

__author__ = 'jpsh'

import time
from random import random, choice, shuffle
from abc import ABCMeta, abstractmethod
from maps import Tile
from maps.grid import GridTools
import time
from functools import wraps

import logging
LOGGING_PREFIX = 'dungeon_generation.cellular_automata.'


class MapGenerationCommand(object):
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


class RandomizeMap(MapGenerationCommand):

    def __init__(self, prob):
        self.prob = prob
        
    def _gen_square(self):
        if random() < self.prob:
            return Tile.EARTH
        else:
            return Tile.FLOOR
    
    def _execute(self, cave):
        actions = []
        for pos in cave.keys():
            actions.append((pos, self._gen_square()))

        cave.batch_set(actions)
        return cave


class SmoothMap(MapGenerationCommand):

    def _execute(self, cave):
        actions = []
        cache = {}
        lst = list(cave.keys())
        shuffle(lst)
        for pos in lst:
            walls = 0
            for pos_r in GridTools.pos_in_radius(pos, 1):
                if (pos in cache and pos[cache] is not Tile.FLOOR) or cave.get(pos_r) is not Tile.FLOOR:
                    walls += 1

            if walls > 5 and cave.get(pos) is Tile.FLOOR:
                actions.append((pos, Tile.EARTH))
                cache[pos] = Tile.EARTH
            elif walls < 4:
                actions.append((pos, Tile.FLOOR))
                cache[pos] = Tile.FLOOR

        cave.batch_set(actions)

        return cave


class HardenWallsMap(MapGenerationCommand):

    def _execute(self, cave):
        flooded = set()
        actions = []
        for pos in cave.keys(tileset=frozenset([Tile.FLOOR])):
            if pos not in flooded:
                actions.extend(self._flood_tile(cave, pos, flooded))

        cave.batch_set(actions)
        return cave

    @staticmethod
    def _flood_tile(cave, pos, flooded):
        actions = []
        queue = [pos]

        while len(queue) > 0:
            pos = queue.pop(0)

            if pos in flooded:
                continue

            tile = cave.get(pos)
            if tile is Tile.FLOOR:
                flooded.add(pos)
                queue.append(GridTools.n(pos))
                queue.append(GridTools.ne(pos))
                queue.append(GridTools.e(pos))
                queue.append(GridTools.se(pos))
                queue.append(GridTools.s(pos))
                queue.append(GridTools.sw(pos))
                queue.append(GridTools.w(pos))
                queue.append(GridTools.nw(pos))

            elif tile is Tile.EARTH:
                actions.append((pos, Tile.WALL))

        return actions


class CloseRooms(MapGenerationCommand):

    def __init__(self, area=1):
        self.area = area
        
    def _execute(self, cave):
        flooded = set()
        actions = []
        for pos in cave.keys(tileset=frozenset([Tile.FLOOR])):
            if pos not in flooded:
                room = self._flood_room(cave, pos)
                if len(room) <= self.area:
                    for cell in room:
                        actions.append((cell, Tile.EARTH))
                flooded.update(room)
        cave.batch_set(actions)
        return cave
    
    @staticmethod
    def _flood_room(cave, pos):
        flooded = set()
        queue = [pos]

        while len(queue) > 0:
            pos = queue.pop(0)

            if pos in flooded:
                continue

            tile = cave.get(pos)
            if tile is Tile.FLOOR:
                flooded.add(pos)
                queue.append(GridTools.n(pos))
                queue.append(GridTools.e(pos))
                queue.append(GridTools.s(pos))
                queue.append(GridTools.w(pos))

        return flooded
    
    
class LinkRooms(MapGenerationCommand):

    def _execute(self, cave):
        all_rooms = self._find_rooms(cave)
        actions = []
        while len(all_rooms) > 1:
            all_rooms.sort(key=lambda x: len(x))

            room = all_rooms.pop(0)
            bb = GridTools.bounding_box(room)
            rooms = []
            extend = 0
            w = cave.width
            h = cave.height
            while len(rooms) == 0:
                extend += 1
                bb = (max(0, bb[0]-extend),
                      max(0, bb[1]-extend),
                      min(w, bb[2]+extend),
                      min(h, bb[3]+extend))
                rooms = self._find_rooms(cave, bounding_box=bb, flooded=room)

            paths = []
            for target_room in rooms:
                path = self._calculate_distance(room, target_room)
                paths.append((path, target_room))
                if path[0] < 4:
                    break

            paths.sort()
            shortest, target_room = paths[0]

            (pos_s, pos_t) = choice(shortest[1])
            corridor = self.dig(pos_s, pos_t)

            for other in all_rooms:
                if target_room.issubset(other):
                    other.update(corridor)
                    other.update(room)
                    break

            for pos in corridor:
                actions.append((pos, Tile.FLOOR))

        cave.batch_set(actions)
        return cave

    @staticmethod
    def dig(start, end):
        xs, ys = start
        xt, yt = end
        dx = xt - xs
        dy = yt - ys

        corridor = [start, end]

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
        min_distance = 1000000
        closest = []
        for pos_a in room_a:
            for pos_b in room_b:
                distance = abs(pos_a[0]-pos_b[0]) + abs(pos_a[1]-pos_b[1])
                if distance < min_distance:
                    min_distance = distance
                    closest = [(pos_a, pos_b)]
                    if min_distance < 3:
                        break
                elif distance == min_distance:
                    closest.append((pos_a, pos_b))

        return min_distance, closest

    def _find_rooms(self, cave, bounding_box=None, flooded=None):
        if not flooded:
            flooded = set()
        else:
            flooded = set(flooded)
        rooms = []

        for pos in cave.keys(tileset=frozenset([Tile.FLOOR]), bb=bounding_box):
            if pos not in flooded:
                room = self._flood_room(cave, pos)
                flooded.update(room)
                rooms.append(room)

        return rooms

    @staticmethod
    def _flood_room(cave, pos):
        room = set()
        queue = [pos]

        while len(queue) > 0:
            pos = queue.pop(0)

            if pos in room:
                continue

            tile = cave.get(pos)
            if tile is Tile.FLOOR:
                room.add(pos)
                queue.append(GridTools.n(pos))
                queue.append(GridTools.e(pos))
                queue.append(GridTools.s(pos))
                queue.append(GridTools.w(pos))

        return room


class MapRender(object):
    __metaclass__ = ABCMeta
        
    @abstractmethod
    def render(self, cave):
        pass
