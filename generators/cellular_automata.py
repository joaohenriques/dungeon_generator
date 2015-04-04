from __future__ import print_function

import os
import sys
import time
from random import random, choice
from enum import Enum
from abc import ABCMeta, abstractmethod
from math import sqrt
from collections import namedtuple

Tile = Enum('Tile', 'UNKNOWN EARTH WALL FLOOR')


class Cave(object):

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
            return self._map[y][x]
        except IndexError:
            # TODO log
            return Tile.UNKNOWN

    def set(self, pos, val):
        x, y = pos
        try:
            self._map[y][x] = val
        except IndexError:
            # TODO log
            pass

    def keys(self, start_pos=None, end_pos=None):
        if not start_pos:
            start_pos = (0, 0)
        if not end_pos:
            end_pos = (self.width, self.height)
        return (Position(x, y) for y in range(start_pos[1], end_pos[1]) for x in range(start_pos[0], end_pos[0]))

    def values(self, start_pos=None, end_pos=None):
        if not start_pos:
            start_pos = (0, 0)
        if not end_pos:
            end_pos = (self.width, self.height)
        return (self._map[y][x] for y in range(start_pos[1], end_pos[1]) for x in range(start_pos[0], end_pos[0]))

    def items(self, start_pos=None, end_pos=None):
        if not start_pos:
            start_pos = (0,0)
        if not end_pos:
            end_pos = (self.width, self.height)
        return ((Position(x, y), self._map[y][x]) for y in range(start_pos[1], end_pos[1]) for x in range(start_pos[0], end_pos[0]))


class Position(namedtuple('Point', ['x', 'y'])):

    def __init__(self, x, y, **kwds):
        super(tuple, self).__init__(x, y, **kwds)

    @property
    def n(self):
        return Position(self.x, self.y-1)

    @property
    def ne(self):
        return Position(self.x+1, self.y-1)

    @property
    def e(self):
        return Position(self.x+1, self.y)

    @property
    def se(self):
        return Position(self.x+1, self.y+1)

    @property
    def s(self):
        return Position(self.x, self.y+1)

    @property
    def sw(self):
        return Position(self.x-1, self.y+1)

    @property
    def w(self):
        return Position(self.x-1, self.y)

    @property
    def nw(self):
        return Position(self.x-1, self.y-1)

    def __repr__(self):
        return "Position(x={}, y={})".format(self.x, self.y)

    def __str__(self):
        return "({}, {})".format(self.x, self.y)


class CaveGenerationCommand(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def execute(self, cave):
        pass
    
    # @abstractmethod
    # def undo(self):
    #     pass


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
            cave.set(pos,self._gen_square())

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
        for pos in cave.keys():
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


class CloseSingleRooms(CaveGenerationCommand):

    def execute(self, cave):
        for pos in cave.keys():
            if cave.get(pos) == Tile.FLOOR and \
               cave.get(pos.s) != Tile.FLOOR and \
               cave.get(pos.e) != Tile.FLOOR:

                if cave.get(pos.sw) == Tile.FLOOR:
                    if random() > 0.5:
                        cave.set(pos.s, Tile.FLOOR)
                    else:
                        cave.set(pos.e, Tile.FLOOR)

                elif cave.get(pos.n) != Tile.FLOOR and \
                        cave.get(pos.w) != Tile.FLOOR:

                    cave.set(pos, Tile.EARTH)

            elif cave.get(pos) != Tile.FLOOR and \
                 cave.get(pos.s) == Tile.FLOOR and \
                 cave.get(pos.e) == Tile.FLOOR and \
                 cave.get(pos.se) != Tile.FLOOR:
                if random() > 0.5:
                    cave.set(pos, Tile.FLOOR)
                else:
                    cave.set(pos.sw, Tile.FLOOR)

        return cave


class LinkRooms(CaveGenerationCommand):

    def __init__(self, crop=0.25):
        self.crop = crop

    def execute(self, cave):
        rooms = self._find_rooms(cave)

        n_rooms = len(rooms)
        if n_rooms > 1:
            distances = {}
            for i in range(0, len(rooms)):
                for j in range(i+1, len(rooms)):
                    room_a = rooms[i]
                    room_b = rooms[j]
                    distances[(i,j)] = self._calculate_distance(room_a, room_b)

            paths = distances.values()
            paths.sort()
            paths = paths[:max(1, int(len(paths) * self.crop))]
            for path in paths:
                (pos_s,pos_t) = choice(path[1])
                cave = self.dig(cave,pos_s,pos_t)

        return cave

    def dig(self, cave, (xs, ys), (xt, yt)):

        if xs == xt and ys == yt:
            return cave

        xd, yd = xs, ys

        if xs != xt:
            if ys != yt and random() > 0.5:
                axis = 'V'
            else:
                axis = 'H'
        else:
            axis = 'V'

        if axis == 'H':
            if xt > xs:
                xd += 1
            elif xt < xs:
                xd -= 1
        else:
            if yt > ys:
                yd += 1
            elif yt < ys:
                yd -= 1

        cave.set((xd,yd), Tile.FLOOR)
        return self.dig(cave, (xd, yd), (xt, yt))

    @staticmethod
    def _calculate_distance(room_a, room_b):
        min_distance = 1000000000.0
        closest = []
        for (xa, ya) in room_a:
            for(xb, yb) in room_b:
                x = abs(xa-xb)
                y = abs(ya-yb)
                distance = sqrt(pow(x,2) + pow(y,2))
                if distance == min_distance:
                    closest.append(((xa, ya), (xb, yb)))
                elif distance < min_distance:
                    min_distance = distance
                    closest = [((xa, ya), (xb, yb))]

        return min_distance, closest
    
    def _find_rooms(self, cave):
        rooms = []
        for pos in cave.keys():
            if cave.get(pos) == Tile.FLOOR:
                in_room = False
                for room in rooms:
                    if pos in room:
                        in_room = True
                        break
                if not in_room:
                    rooms.append(self._it_flood_room(cave, pos))

        return rooms

    @staticmethod
    def _it_flood_room(cave, pos):
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
            elif val == Tile.DIG:
                str_buffer.append('.')
            #elif val == Tile.SAND:
            #    buffer.append('.')
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


def main():

    WIDTH = 77
    HEIGHT= 20
    PROB = 0.4

    cave = Cave(HEIGHT, WIDTH)
    creator = RandomizeCave(PROB)
    smooth = SmoothCave()
    closerooms = CloseSingleRooms()
    flood = HardenWallsCave()
    linkroom = LinkRooms(.2)
    
    renderer = TextRenderer()
    animator = Animator(renderer, cave)

    animator.add_command(creator)
    animator.add_command(smooth)
    animator.add_command(closerooms)
    animator.add_command(linkroom)
    animator.add_command(linkroom)
    animator.add_command(linkroom)
    animator.add_command(linkroom)
    animator.add_command(linkroom)
    animator.add_command(linkroom)
    animator.add_command(flood)
    
    animator.animate(delay=0.1)
    
if __name__ == '__main__':
    main()
