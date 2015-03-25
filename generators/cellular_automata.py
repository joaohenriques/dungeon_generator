
from random import random
from enum import Enum

Tile = Enum('Tile', 'EARTH GROUND WALL FLOOR')

UNKNOWN = '*'
WALL = '#'
EARTH = '+'
WET_EARTH = '~'
DRY_EARTH = '%'
GROUND = '.'
FLOOR = ' '

def gen_square(prob):
    if random() >= prob:
        return UNKNOWN
    else:
        return GROUND


def gen_dungeon(height=10, width=10, prob=0.4):
    
    dungeon = []
    outerwall = [WALL for _ in range(0,width)]
    dungeon.append(outerwall)
    for row in range(0, height-2):
        line = [gen_square(prob) for _ in range(0,width-2)]
        #add outer wall
        line.append(WALL)
        line.insert(0, WALL)
        dungeon.append(line)
    dungeon.append(outerwall)
    return dungeon

def evolve_dungeon(dungeon):
    for y in range(1,len(dungeon)-1):
        for x in range(1,len(dungeon[y])-1):
                       
            walls = 0
            if dungeon[y-1][x-1] != GROUND:
                walls += 1
            if dungeon[y-1][x] != GROUND:
                walls += 1
            if dungeon[y-1][x+1] != GROUND:
                walls += 1

            if dungeon[y][x-1] != GROUND:
                walls += 1
            if dungeon[y][x+1] != GROUND:
                walls += 1

            if dungeon[y+1][x-1] != GROUND:
                walls += 1
            if dungeon[y+1][x] != GROUND:
                walls += 1
            if dungeon[y+1][x+1] != GROUND:
                walls += 1

            if walls > 5:
                dungeon[y][x] = EARTH
            elif walls < 4:
                dungeon[y][x] = GROUND
                       
    return dungeon

def clean_dungeon(dungeon, orig, dest):
    for y in range(1,len(dungeon)-1):
        for x in range(1,len(dungeon[y])-1):
            if dungeon[y][x] == orig:
                 dungeon[y][x] = dest
    return dungeon

def flood_dungeon(dungeon):
    for y in range(1,len(dungeon)-1):
        for x in range(1,len(dungeon[y])-1):
            if dungeon[y][x] == GROUND:
                dungeon = flood_dungeon_tile(dungeon, (x,y))
                dungeon = clean_dungeon(dungeon, WET_EARTH, DRY_EARTH)

    return dungeon

def flood_dungeon_tile(dungeon, pos):
    x,y = pos
    tile = dungeon[y][x]
    if tile == GROUND:
        dungeon[y][x] = FLOOR
        dungeon = flood_dungeon_tile(dungeon, (x,y-1))
        dungeon = flood_dungeon_tile(dungeon, (x-1,y))
        dungeon = flood_dungeon_tile(dungeon, (x+1,y))
        dungeon = flood_dungeon_tile(dungeon, (x,y+1))
    elif tile == EARTH:
        dungeon[y][x] = WET_EARTH
    elif tile == DRY_EARTH:
        dungeon[y][x] = UNKNOWN

    return dungeon
    
def print_dungeon(dungeon):
    for line in dungeon:
        linestr = []
        for char in line:
            if char == GROUND:
                linestr.append(FLOOR)
            else:
                linestr.append(WALL)
        print("".join(linestr))
    print("")
    
def dump_dungeon(dungeon):
    for line in dungeon:
        print("".join(line))
    print("")
    
def gen1():
    dungeon = gen_dungeon(17,60,.40)
    for i in range(0,3):
        dungeon = evolve_dungeon(dungeon)
    dungeon = clean_dungeon(dungeon, UNKNOWN, GROUND)
    dungeon = flood_dungeon(dungeon)
    dungeon = clean_dungeon(dungeon, DRY_EARTH, WALL)
    dungeon = clean_dungeon(dungeon, UNKNOWN, FLOOR)
    
    dump_dungeon(dungeon)

def gen2():
    dungeon = gen_dungeon(17,30,.40)
    print_dungeon(dungeon)
    dungeon = evolve_dungeon(dungeon)
    dump_dungeon(dungeon)
    dungeon = clean_dungeon(dungeon, UNKNOWN, GROUND)
    dungeon = flood_dungeon(dungeon)
    dungeon = clean_dungeon(dungeon, DRY_EARTH, WALL)
    dungeon = clean_dungeon(dungeon, UNKNOWN, FLOOR)
    dump_dungeon(dungeon)
        
if __name__ == '__main__':
    gen1()
