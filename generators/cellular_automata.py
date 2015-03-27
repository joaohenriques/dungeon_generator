from __future__ import print_function

import os,sys,time
from random import random
from enum import Enum
import copy

Tile = Enum('Tile', 'EARTH WALL FLOOR')



class MapTransform(object):
    def transform(self, map):
        raise NotImplemented

class RandomizeMap(MapTransform):

    def __init__(self,prob):
        self.prob = prob
        
    def _gen_square(self):
        if random() >= self.prob:
            return Tile.EARTH
        else:
            return Tile.FLOOR
    
    def transform(self, map):
        height = len(map)
        width = len(map[0])

        # first and last lines
        for x in range(0,width):
            map[0][x] = Tile.WALL
            map[-1][x] = Tile.WALL

        # other lines
        for line in map[1:-1]:
            line[0] = Tile.WALL
            line[-1] = Tile.WALL
            for x in range(1, width-1):
                line[x] = self._gen_square()

        return map

class SmoothMap(MapTransform):

    def transform(self,map):
        for y in range(1,len(map)-1):
            for x in range(1,len(map[y])-1):
                       
                walls = 0
                if map[y-1][x-1] != Tile.FLOOR:
                    walls += 1
                if map[y-1][x] != Tile.FLOOR:
                    walls += 1
                if map[y-1][x+1] != Tile.FLOOR:
                    walls += 1

                if map[y][x-1] != Tile.FLOOR:
                    walls += 1
                if map[y][x+1] != Tile.FLOOR:
                    walls += 1

                if map[y+1][x-1] != Tile.FLOOR:
                    walls += 1
                if map[y+1][x] != Tile.FLOOR:
                    walls += 1
                if map[y+1][x+1] != Tile.FLOOR:
                    walls += 1

                if walls > 5:
                    map[y][x] = Tile.EARTH
                elif walls < 4:
                    map[y][x] = Tile.FLOOR
                       
        return map

class HardenWallsMap(MapTransform):

    def transform(self, map):
        flooded = set()
        for y in range(1,len(map)-1):
            for x in range(1,len(map[y])-1):
                if map[y][x] == Tile.FLOOR:
                    map = self._flood_tile(map, (x,y), flooded)
        return map

    def _flood_tile(self, map, pos, flooded):
        if pos in flooded:
            return map

        x,y = pos
        tile = map[y][x]
        if tile == Tile.FLOOR:
            flooded.add(pos)
            map = self._flood_tile(map, (x,y-1), flooded)
            map = self._flood_tile(map, (x-1,y), flooded)
            map = self._flood_tile(map, (x+1,y), flooded)
            map = self._flood_tile(map, (x,y+1), flooded)
        elif tile == Tile.EARTH:
            map[y][x] = Tile.WALL
        return map

class MapRender(object):

    def add_map(self, map):
        raise NotImplemented
    def render(self, map):
        raise NotImplemented

class TextRenderer(MapRender):
        
    def render(self, map):
        buffer = []
        for line in map:
            for pos in line:
                if pos == Tile.WALL:
                    buffer.append('#')
                elif pos == Tile.FLOOR:
                    buffer.append(' ')
                elif pos == Tile.EARTH:
                    buffer.append('+')
                elif pos == Tile.WET:
                    buffer.append('~')
                elif pos == Tile.SAND:
                    buffer.append('.')
                else:
                    buffer.append('?')
            buffer.append(os.linesep)
        return "".join(buffer)
    
class Animator(object):

    def __init__(self, renderer):
        self.renderer = renderer
        self.maps = []

    def _clear_console(self):
        if os.name == 'posix':
            os.system('clear')
        else:
            os.system('CLS')
            
    def add_map(self, map, deepcopy=False):
        if deepcopy:
            self.maps.append(copy.deepcopy(map))
        else:
            self.maps.append(map)

    def animate(self, delay=1):
        for map in self.maps:
            # Clear the console
            self._clear_console()

            outstr = self.renderer.render(map)
            # Write the current frame on stdout and sleep
            
            sys.stdout.write(outstr)
            sys.stdout.flush()
            time.sleep(delay)    

def main():

    WIDTH = 40
    HEIGHT= 25
    PROB = 0.4
    
    map = [[None for _ in range(0, WIDTH)] for _ in range(0, HEIGHT)]
    
    creator = RandomizeMap(PROB)
    smooth = SmoothMap()
    flood = HardenWallsMap()
    renderer = TextRenderer()
    animator = Animator(renderer)

    map = creator.transform(map)
    animator.add_map(map,True)
    
    map = smooth.transform(map)
    animator.add_map(map,True)

    # map = smooth.transform(map)
    # animator.add_map(map,True)

    map = flood.transform(map)
    animator.add_map(map,True)
    
    animator.animate()    
    
if __name__ == '__main__':
    main()
