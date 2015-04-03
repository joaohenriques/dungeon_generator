from __future__ import print_function

import os
import sys
import time
from random import random, choice
from enum import Enum
from abc import ABCMeta, abstractmethod
from math import sqrt

Tile = Enum('Tile', 'EARTH WALL FLOOR ROOM')


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
        width = len(cave[0])

        # first and last lines
        for x in range(0, width):
            cave[0][x] = Tile.WALL
            cave[-1][x] = Tile.WALL

        # other lines
        for line in cave[1:-1]:
            line[0] = Tile.WALL
            line[-1] = Tile.WALL
            for x in range(1, width-1):
                line[x] = self._gen_square()

        return cave


class SmoothCave(CaveGenerationCommand):

    def execute(self, cave):
        for y in range(1, len(cave)-1):
            for x in range(1, len(cave[y])-1):
                       
                walls = 0
                if cave[y-1][x-1] != Tile.FLOOR:
                    walls += 1
                if cave[y-1][x] != Tile.FLOOR:
                    walls += 1
                if cave[y-1][x+1] != Tile.FLOOR:
                    walls += 1

                if cave[y][x-1] != Tile.FLOOR:
                    walls += 1
                if cave[y][x+1] != Tile.FLOOR:
                    walls += 1

                if cave[y+1][x-1] != Tile.FLOOR:
                    walls += 1
                if cave[y+1][x] != Tile.FLOOR:
                    walls += 1
                if cave[y+1][x+1] != Tile.FLOOR:
                    walls += 1

                if walls > 5:
                    cave[y][x] = Tile.EARTH
                elif walls < 4:
                    cave[y][x] = Tile.FLOOR
                       
        return cave


class HardenWallsCave(CaveGenerationCommand):

    def execute(self, cave):
        flooded = set()
        for y in range(1, len(cave)-1):
            for x in range(1, len(cave[y])-1):
                if cave[y][x] == Tile.FLOOR:
                    cave = self._flood_tile(cave, (x, y), flooded)
        return cave

    def _flood_tile(self, cave, pos, flooded):
        if pos in flooded:
            return cave

        x,y = pos
        tile = cave[y][x]
        if tile == Tile.FLOOR:
            flooded.add(pos)
            cave = self._flood_tile(cave, (x,y-1), flooded)
            cave = self._flood_tile(cave, (x-1,y), flooded)
            cave = self._flood_tile(cave, (x+1,y), flooded)
            cave = self._flood_tile(cave, (x,y+1), flooded)
        elif tile == Tile.EARTH:
            cave[y][x] = Tile.WALL
        return cave


class CloseSingleRooms(CaveGenerationCommand):

    def execute(self, cave):
        for y in range(1, len(cave)-1):
            for x in range(1, len(cave[y])-1):
                if cave[y][x] == Tile.FLOOR and \
                   cave[y+1][x] == Tile.EARTH and \
                   cave[y][x+1] == Tile.EARTH:

                    if cave[y+1][x+1] == Tile.FLOOR:
                        if random() > 0.5:
                            cave[y+1][x] = Tile.FLOOR
                        else:
                            cave[y][x+1] = Tile.FLOOR

                    elif cave[y-1][x] == Tile.EARTH and \
                       cave[y][x-1] == Tile.EARTH:

                        cave[y][x] = Tile.EARTH

                elif cave[y][x] == Tile.EARTH and \
                   cave[y+1][x] == Tile.FLOOR and \
                   cave[y][x+1] == Tile.FLOOR and \
                   cave[y+1][x+1] == Tile.EARTH:
                    if random() > 0.5:
                        cave[y][x] = Tile.FLOOR
                    else:
                        cave[y+1][x+1] = Tile.FLOOR

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

        axis = 'H'
        if xs != xt:
            if ys != yt and random() > 0.5:
                axis = 'V'
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

        cave[yd][xd] = Tile.FLOOR
        return self.dig(cave,(xd,yd),(xt,yt))

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
                    closest.append(((xa,ya),(xb,yb)))
                elif distance < min_distance:
                    min_distance = distance
                    closest = [((xa,ya),(xb,yb))]

        return (min_distance, closest)
    
    def _find_rooms(self, cave):
        rooms = []
        for y in range(1,len(cave)-1):
            for x in range(1,len(cave[y])-1):
                if cave[y][x] == Tile.FLOOR:
                    pos = (x,y)
                    in_room = False
                    for room in rooms:
                        if pos in room:
                            in_room = True
                            break
                    if not in_room:
                        rooms.append(self._flood_tile(cave, pos))

        return rooms
    
    def _flood_tile(self, cave, pos, flooded=None):
        if not flooded:
            flooded = set()
        x,y = pos
        if pos not in flooded and cave[y][x] == Tile.FLOOR:
            flooded.add(pos)
            flooded = self._flood_tile(cave, (x,y-1), flooded)
            flooded = self._flood_tile(cave, (x-1,y), flooded)
            flooded = self._flood_tile(cave, (x+1,y), flooded)
            flooded = self._flood_tile(cave, (x,y+1), flooded)

        return flooded


class MapRender(object):
    __metaclass__=ABCMeta
        
    @abstractmethod
    def render(self, cave):
        pass


class TextRenderer(MapRender):
        
    def render(self, cave):
        str_buffer = []
        for line in cave:
            for pos in line:
                if pos == Tile.WALL:
                    str_buffer.append('#')
                elif pos == Tile.FLOOR:
                    str_buffer.append(' ')
                elif pos == Tile.EARTH:
                    str_buffer.append('+')
                elif pos == Tile.DIG:
                    str_buffer.append('.')
                #elif pos == Tile.SAND:
                #    buffer.append('.')
                else:
                    str_buffer.append(str(pos))
            str_buffer.append(os.linesep)
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

    WIDTH = 80
    HEIGHT= 20
    PROB = 0.4
    
    map = [[None for _ in range(0, WIDTH)] for _ in range(0, HEIGHT)]

    creator = RandomizeCave(PROB)
    smooth = SmoothCave()
    closerooms = CloseSingleRooms()
    flood = HardenWallsCave()
    linkroom = LinkRooms(0.20)
    
    renderer = TextRenderer()
    animator = Animator(renderer, map)

    animator.add_command(creator)
    animator.add_command(smooth)
    animator.add_command(closerooms)
    animator.add_command(linkroom)
    animator.add_command(linkroom)
    animator.add_command(linkroom)
    animator.add_command(linkroom)
    animator.add_command(linkroom)
    animator.add_command(flood)
    
    animator.animate(delay=0.2)
    
if __name__ == '__main__':
    main()
