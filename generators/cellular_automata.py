from __future__ import print_function

__author__ = 'jpsh'

import os
import sys
import time
from random import random, choice
from abc import ABCMeta, abstractmethod
from common import Tile
from common.maps import Square

class CaveGenerationCommand(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def execute(self, cave):
        pass


class RandomizeCave(CaveGenerationCommand):

    def __init__(self, prob):
        self.prob = prob
        
    def _gen_square(self):
        if random() >= self.prob:
            return Tile.EARTH
        else:
            return Tile.FLOOR
    
    def execute(self, cave):

        for pos in cave.keys():
            cave.set(pos, self._gen_square())

        return cave


class SmoothCave(CaveGenerationCommand):

    def execute(self, cave):
        for pos in cave.keys():
            walls = 0
            if cave.get(pos.nw) != Tile.FLOOR:
                walls += 1
            if cave.get(pos.n) != Tile.FLOOR:
                walls += 1
            if cave.get(pos.ne) != Tile.FLOOR:
                walls += 1

            if cave.get(pos.w) != Tile.FLOOR:
                walls += 1
            if cave.get(pos.e) != Tile.FLOOR:
                walls += 1

            if cave.get(pos.sw) != Tile.FLOOR:
                walls += 1
            if cave.get(pos.s) != Tile.FLOOR:
                walls += 1
            if cave.get(pos.se) != Tile.FLOOR:
                walls += 1

            if walls > 5:
                cave.set(pos, Tile.EARTH)
            elif walls < 4:
                cave.set(pos, Tile.FLOOR)
                       
        return cave


class HardenWallsCave(CaveGenerationCommand):

    def execute(self, cave):
        flooded = set()
        for pos in cave.keys(filter_expr=lambda x: x == Tile.FLOOR):
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
                stack.append(pos.n)
                stack.append(pos.e)
                stack.append(pos.s)
                stack.append(pos.w)

            elif tile == Tile.EARTH:
                cave.set(pos, Tile.WALL)

        return cave


class CloseOneSquareRooms(CaveGenerationCommand):

    def execute(self, cave):
        for pos in cave.keys(filter_expr=lambda x: x == Tile.FLOOR):
            if (cave.get(pos) == Tile.FLOOR and
                    cave.get(pos.s) != Tile.FLOOR and
                    cave.get(pos.e) != Tile.FLOOR and
                    cave.get(pos.n) != Tile.FLOOR and
                    cave.get(pos.w) != Tile.FLOOR):

                cave.set(pos, Tile.EARTH)

        return cave


class LinkRooms(CaveGenerationCommand):

    def execute(self, cave):
        rooms = self._find_rooms(cave)

        while len(rooms) > 1:
            paths = []
            for i in range(0, len(rooms)):
                for j in range(i+1, len(rooms)):
                    room_a = rooms[i]
                    room_b = rooms[j]
                    path = self._calculate_distance(room_a, room_b)
                    paths.append((path, (i, j)))
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
    def dig((xs, ys), (xt, yt)):
        dx = xt - xs
        dy = yt - ys

        corridor = []

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
            corridor.append(Square(x, y))

        return corridor

    @staticmethod
    def _calculate_distance(room_a, room_b):
        min_distance = 1000000000.0
        closest = []
        for pos_a in room_a:
            for pos_b in room_b:
                distance = pos_a.distance(pos_b)
                if distance == min_distance:
                    closest.append((pos_a, pos_b))
                elif distance < min_distance:
                    min_distance = distance
                    closest = [(pos_a, pos_b)]

        return min_distance, closest

    def _find_rooms(self, cave, rooms=None):
        if not rooms:
            rooms = []

        for pos in cave.keys(filter_expr=lambda x: x == Tile.FLOOR):
            in_room = False
            for room in rooms:
                if pos in room:
                    in_room = True
                    break
            if not in_room:
                rooms.append(self._flood_room(cave, pos))

        return rooms

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
                stack.append(pos.n)
                stack.append(pos.e)
                stack.append(pos.s)
                stack.append(pos.w)

        return room


class MapRender(object):
    __metaclass__ = ABCMeta
        
    @abstractmethod
    def render(self, cave):
        pass


class TextRenderer(MapRender):
        
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
                str_buffer.append(str(val))

            if col % width == 0:
                col = 0
                str_buffer.append("#")
                str_buffer.append("\n")
                str_buffer.append("#")
        str_buffer.append("#" * (width+1))

        return "".join(str_buffer)


class Animator(object):

    def __init__(self, renderer, cave):
        self.renderer = renderer
        self.command_queue = []
        self.cave = cave

    @staticmethod
    def _clear_console():
        if os.name == 'posix':
            os.system('clear')
        else:
            os.system('CLS')
            
    def add_command(self, command):
        self.command_queue.append(command)

    def animate(self, delay=1):
        for command in self.command_queue:

            self.cave = command.execute(self.cave)
            out_str = self.renderer.render(self.cave)

            # Clear the console
            self._clear_console()
            # Write the current frame on stdout and sleep
            sys.stdout.write(out_str)
            sys.stdout.flush()
            time.sleep(delay)
