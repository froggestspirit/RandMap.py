#!/usr/bin/python3

'''
Overview/Notes: Generates a random sized map, and exit placement. Each block will represent 4x4 tiles in-game.
Using the positionings of the exits, a "center" point will be determined, where all paths from the exits will try to meet up there
Paths will stop if they intersect with another path that's been drawn.
Any entities that must be in the map (for example Pokemon Centers or Marts) will be randomly placed, and have a path created as well.
Since there are potential issues of entities paths overwriting the entity that was previously made, the map will be flagged as a bad map.
Any other issues that could arise during generation that would be an issue for the map, but take more time to fix or workaround can be flagged as a bad map.

After entities and paths are made, other items (trees, water, etc) can be placed. The idea is that these things can be placed anywhere (besides the path and margins)
and the player will still be able to access all areas needed.

When starting a new game, every map (town, city, route, etc) will have a seed assigned to it, which will be stored in the save.
This way, at new game, the generation code can take the time to run through each seed, make sure it's not a bad map, or regenerate if it is.
When the save is created, every map should have a "good map" seed it can use to generate the same map everytime it is visited
'''
import sys
import pygame
from pygame.locals import *

WINSIZE = (30, 30)
WINSIZESCALE = (960, 960)
seed = 0
mapType = None
MAX_REROLLS = 10  # RNG can sometimes get stuck (especially on entity placement). Give up if this number of re-rolls is reached, and mark the map "bad"
debug = True
badMap = False

if len(sys.argv) > 1:
    seed = int(sys.argv[1])
if len(sys.argv) == 3:
    mapType = int(sys.argv[2])
def dprint(string):  # Set debug = True for the dprint items to show
    global debug
    if(debug):
        print(string)


def rand(a, b):  # Psuedo Random number generator, using the same formula as the Gen 3/4 games
    global seed
    seed = ((0x41C64E6D * seed) + 0x00006073) & 0xFFFFFFFF
    if(a > b):
        return ((seed >> 16) % ((a - b) + 1)) + b
    return ((seed >> 16) % ((b - a) + 1)) + a


def read_input():  # Input handling (space to generate a new map, or esc/close to exit)
    for e in pygame.event.get():
        if e.type == QUIT or (e.type == KEYUP and e.key == K_ESCAPE):
            buffer.close()
            quit()
        if (e.type == KEYUP and e.key == K_SPACE):
            return True


def check_rect(tile, x, y, w, h):  # Check if a rectangle is free of tiles that are not tile, or 0
    if x + w < x:
        x = x + w
        w = abs(w)
    if y + h < y:
        y = y + h
        h = abs(h)
    for yi in range(h):
        yCoord = y + yi
        for xi in range(w):
            xCoord = x + xi
            if(mapData[(yCoord * width) + xCoord] != tile):
                if(mapData[(yCoord * width) + xCoord]):
                    return False
    return True


def fill_rect(tile, x, y, w, h):  # Fill a rectangle with tile
    if x + w < x:
        x = x + w
        w = abs(w)
    if y + h < y:
        y = y + h
        h = abs(h)
    for yi in range(h):
        yCoord = y + yi
        for xi in range(w):
            xCoord = x + xi
            if(not mapData[(yCoord * width) + xCoord]):
                mapData[(yCoord * width) + xCoord] = tile


def draw_line(tile, x1, y1, x2, y2):  # Draw a line of tiles (this expects either a horizantal/vertical line, not diagonal)
    global badMap
    count = 0
    inc = [0,0]
    if x1 < x2:
        inc[0] = 1
    if y1 < y2:
        inc[1] = 1
    if x1 > x2:
        inc[0] = -1
    if y1 > y2:
        inc[1] = -1
    while (x1 != x2) or (y1 != y2):
        if(mapData[(y1 * width) + x1] == tile):
            return True
        if(mapData[(y1 * width) + x1] >= 4):  # drew a path over an entity
            badMap = True
            return True
        mapData[(y1 * width) + x1] = tile
        if(count):
            if(mapData[((y1 + inc[0]) * width) + (x1 + inc[1])] == tile):
                return True
            if(mapData[((y1 - inc[0]) * width) + (x1 - inc[1])] == tile):
                return True
        x1 += inc[0]
        y1 += inc[1]
        count += 1
    if(mapData[(y1 * width) + x1] == tile):
        return True
    return False


def process_path(dir, point, destPoint):  # Handle drawing the paths
    PATH_LINEARITY = 4 # Paths will move a minimum of this number of tiles before turning (unless it's destination is closer)
    dprint(f"Starting path {point} to {destPoint} starting {dir}")
    while (point[0] != destPoint[0]) or (point[1] != destPoint[1]):
        if(abs(destPoint[dir] - point[dir]) > PATH_LINEARITY):
            len = rand(PATH_LINEARITY, abs(destPoint[dir] - point[dir]))
            dprint(f"Rand call, len: {len}")
        else:
            len = abs(destPoint[dir] - point[dir])
        if(len):
            xy = [point[0], point[1]]
            xy2 = [point[0], point[1]]
            if(destPoint[dir] < point[dir]):
                len = -len
            xy2[dir] += len 
            point[dir] += len
            if(draw_line(2, xy[0], xy[1], xy2[0], xy2[1])):
                point[0] = destPoint[0]
                point[1] = destPoint[1]
            dprint(f"Path point {point}")
        dir ^= 1


# Main entry point of code
print("\nPress space to generate a new map")
clock = pygame.time.Clock()
#initialize and prepare screen
pygame.init()
screen = pygame.display.set_mode(WINSIZESCALE)
s = pygame.Surface(WINSIZE)
s2 = pygame.Surface(WINSIZESCALE)
buffer = pygame.PixelArray(s)

color = [0xA0E0A0, 0x303030, 0xFFFFFF, 0x00A030, 0xFF0000, 0x0000FF]
mainDone = 0
while not mainDone:
    if badMap:
        seed = (backupSeed + 1) & 0xFFFFFFFF
    backupSeed = seed
    print(f"Seed: {hex(seed)}")
    badMap = False
    for y in range(WINSIZE[0]):
        for x in range(WINSIZE[1]):
            buffer[x, y] = 0
    # Maps are built in blocks first that represent 4x4 tiles
    # Map size
    width = rand(8,30)
    height = rand(8,30)
    size = ((width * 4) + 15) * ((height * 4) + 14)
    # Enforce maximum size (In-game RAM limit)
    while size >= 0x2800:
        dprint("Re-roll size")
        if height >= width:
            height -= 1
        else:
            width -= 1
        size = ((width * 4) + 15) * ((height * 4) + 14)

    # Map type, exits, should be defined beforehand, but here they are randomly generated for example's sake
    MARGIN_SIZE = 2
    if mapType is None:
        mapType = rand(0,15)
    exitPos = [0, 0, 0, 0]
    exitSize = [0, 0, 0, 0]
    mapDim = [width, height, width, height]
    bit = 1
    for i in range(4):
        if mapType & bit:
            exitPos[i] = rand(MARGIN_SIZE, (mapDim[i] - 1) - MARGIN_SIZE)
            exitSize[i] = rand(1, 4)
            if (exitPos[i] + (exitSize[i])) >= (mapDim[i] - MARGIN_SIZE):
                exitPos[i] -= (exitPos[i] + exitSize[i]) - (mapDim[i] - MARGIN_SIZE)
        bit *= 2

    # Create a bare map template
    mapData = []
    for y in range(height):
        for x in range(width):
            # Get location type corners will be borders, margins may vary, center has no border
            locType = 0
            if y >= MARGIN_SIZE:
                locType += 3
            if y >= (height - MARGIN_SIZE):
                locType += 3
            if x >= MARGIN_SIZE:
                locType += 1
            if x >= (width - MARGIN_SIZE):
                locType += 1

            if locType in(0,2,6,8):    
                mapData.append(1)
            elif locType == 4:
                mapData.append(0)
            elif locType == 1:
                if (x >= exitPos[0]) and (x < exitPos[0] + (exitSize[0])):
                    mapData.append(0)
                else:
                    mapData.append(1)
            elif locType == 3:
                if (y >= exitPos[1]) and (y < exitPos[1] + (exitSize[1])):
                    mapData.append(0)
                else:
                    mapData.append(1)
            elif locType == 5:
                if (y >= exitPos[3]) and (y < exitPos[3] + (exitSize[3])):
                    mapData.append(0)
                else:
                    mapData.append(1)
            elif locType == 7:
                if (x >= exitPos[2]) and (x < exitPos[2] + (exitSize[2])):
                    mapData.append(0)
                else:
                    mapData.append(1)

    # Set focal points for the path
    # Create one near each exit, and one near the center
    pathPointCenter = [int(width / 2), int(height / 2)]
    pathPoint = []
    firstDir = []
    xyAvg = [0, 0]
    points = 0

    if exitPos[0] > 0:
        pathPoint.append([exitPos[0] + int(exitSize[0] / 2), MARGIN_SIZE])
        firstDir.append(1)
        xyAvg[0] -= pathPoint[points][0]
        xyAvg[1] -= pathPoint[points][1]
        print(pathPoint[points])
        points += 1
    if exitPos[1] > 0:
        pathPoint.append([MARGIN_SIZE, exitPos[1] + int(exitSize[1] / 2)])
        firstDir.append(0)
        xyAvg[0] -= pathPoint[points][0]
        xyAvg[1] -= pathPoint[points][1]
        print(pathPoint[points])
        points += 1
    if exitPos[2] > 0:
        pathPoint.append([exitPos[2] + int(exitSize[2] / 2), height - (MARGIN_SIZE + 1)])
        firstDir.append(1)
        xyAvg[0] -= pathPoint[points][0]
        xyAvg[1] -= pathPoint[points][1]
        print(pathPoint[points])
        points += 1
    if exitPos[3] > 0:
        pathPoint.append([width - (MARGIN_SIZE + 1), exitPos[3] + int(exitSize[3] / 2)])
        firstDir.append(0)
        xyAvg[0] -= pathPoint[points][0]
        xyAvg[1] -= pathPoint[points][1]
        print(pathPoint[points])
        points += 1

    # Adjust the center point so there's less blank space
    if(points):
        xyAvg[0] = int(xyAvg[0] / points) - 1
        xyAvg[1] = int(xyAvg[1] / points) - 1
        if(xyAvg[0] < MARGIN_SIZE):
            xyAvg[0] += width
        if(xyAvg[1] < MARGIN_SIZE):
            xyAvg[1] += height
        pathPointCenter = [xyAvg[0], xyAvg[1]]
        print(pathPointCenter)

    # Create buildings or entities that should spawn a path point
    entity = [4, 5] # Example Pokemon Center, then Mart
    entityPos = []

    # Draw the path with the path points
    for i, point in enumerate(pathPoint):
        print(f"ProcessPath{i}: {hex(seed)}")
        process_path(firstDir[i], point, pathPointCenter)
    mapData[(pathPointCenter[1] * width) + pathPointCenter[0]] = 2

    # If the generator detects something is wrong with the map, it will be flagged, so it can be disregarded in new game creation
    if(badMap):
        print("Bad Map")
        continue    

    # Find space for the entities
    for i, obj in enumerate(entity):
        entityPos.append([0,0])
        xy = [0,0]
        rerolls = 0
        while entityPos[i] == [0,0]:
            if(rerolls > MAX_REROLLS): # Too many re-rolls, abort
                entityPos[i] = [1,1]
                badMap = True
            else:
                rerolls += 1
                xy[0] = rand(MARGIN_SIZE, (width - 1) - MARGIN_SIZE)
                xy[1] = rand(MARGIN_SIZE, (height - 2) - MARGIN_SIZE)
                dprint(f"Re-roll entity pos:{seed} ({MARGIN_SIZE}, {(width - 1) - MARGIN_SIZE}) x ({MARGIN_SIZE}, {(height - 2) - MARGIN_SIZE}) : {xy}")
                if(xy[0] == pathPointCenter[0]):
                    xy[0] += 1
                if(xy[1] == pathPointCenter[1]):
                    xy[1] += 1
                if(check_rect(0, xy[0], xy[1] - 1, 1, 2)): # Make sure the area the entity is placed is clear, and the tile above it
                    if(check_rect(2, xy[0], xy[1] + 1, 1, 1)): # Do a separate check for the tile below the entity, alowing paths, since they are good to lead up to buildings
                        entityPos[i] = [xy[0], xy[1]]
                        mapData[(xy[1] * width) + xy[0]] = obj
    
    # If the generator detects something is wrong with the map, it will be flagged, so it can be disregarded in new game creation
    if(badMap):
        print("Bad Map")
        continue

    # Create paths for the entities
    for i, point in enumerate(entityPos):
        point[1] += 1
        process_path(0, point, pathPointCenter)
    
    # If the generator detects something is wrong with the map, it will be flagged, so it can be disregarded in new game creation
    if(badMap):
        print("Bad Map")
        continue

    # Draw tiles to the main buffer
    for y in range(height):
        for x in range(width):
            buffer[x, y] = color[mapData[(y * width) + x]]

    # Main loop
    done = 0
    print(f"EndingSeed: {hex(seed)}")
    while not done:
        pygame.transform.scale(s, WINSIZESCALE, s2)
        screen.blit(s2,(0,0))
        pygame.display.update()
        done = read_input()
        if(badMap): # Automatically skip a bad map and generate a new one
            done = 1
            
