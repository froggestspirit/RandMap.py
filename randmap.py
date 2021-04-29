#!/usr/bin/python3

import random as rand
import os, sys, math, pygame
from pygame.locals import *

WINSIZE = [30, 30]
WINSIZESCALE = [960, 960]

def read_input():
    for e in pygame.event.get():
        if e.type == QUIT or (e.type == KEYUP and e.key == K_ESCAPE):
            buffer.close()
            sys.exit()
        if (e.type == KEYUP and e.key == K_LEFT):
            return True
            break

def check_rect(tile, x, y, w, h):
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
            if(mapData[(yCoord * width) + xCoord] == tile):
                return True
    return False

def draw_line(tile, x1, y1, x2, y2):
    inc = [1,1]
    if x1 == x2:
        inc[0] = 0
    if y1 == y2:
        inc[1] = 0
    if x1 > x2:
        inc[0] = -1
    if y1 > y2:
        inc[1] = -1
    while (x1 != x2) and (y1 != y2):
        print(x1)
        if(mapData[(y1 * width) + x1] == tile):
            return True
        mapData[(y1 * width) + x1] = tile
        x1 += inc[0]
        y1 += inc[1]
    mapData[(y1 * width) + x1] = tile
    return False

clock = pygame.time.Clock()
#initialize and prepare screen
pygame.init()
screen = pygame.display.set_mode(WINSIZESCALE)
s = pygame.Surface(WINSIZE)  # the size of your rect
s2 = pygame.Surface(WINSIZESCALE)
color = [0xA0E0A0, 0x303030, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0x00A030]
buffer = pygame.PixelArray(s)

mainDone = 0
while not mainDone:
    for y in range(WINSIZE[0]):
        for x in range(WINSIZE[1]):
            buffer[x, y] = 0
    # Maps are built in blocks first that represent 4x4 tiles
    #Map size
    width = rand.randint(8,30)
    height = rand.randint(8,30)
    size = ((width * 4) + 15) * ((height * 4) + 14)
    #Enforce maximum size
    while size >= 0x2800:
        if height >= width:
            height -= 1
        else:
            width -= 1
        size = ((width * 4) + 15) * ((height * 4) + 14)


    #Map type, exits, should be defined beforehand
    MARGIN_SIZE = 2
    mapType = rand.randint(0,15)
    exitPos = [0, 0, 0, 0]
    exitSize = [0, 0, 0, 0]
    mapDim = [width, height, width, height]
    bit = 1
    for i in range(4):
        if mapType & bit:
            exitPos[i] = rand.randint(MARGIN_SIZE, (mapDim[i] - 1) - MARGIN_SIZE)
            exitSize[i] = rand.randint(1, 4)
            if (exitPos[i] + (exitSize[i])) >= (mapDim[i] - MARGIN_SIZE):
                exitPos[i] -= (exitPos[i] + exitSize[i]) - (mapDim[i] - MARGIN_SIZE)
        bit *= 2
    print(f"{width} by {height}")


    # Create a bare map template
    mapData = []
    for y in range(height):
        for x in range(width):
            #Get location type corners will be borders, margins may vary, center has no border
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

    if exitPos[0] > 0:
        pathPoint.append([exitPos[0] + int(exitSize[0] / 2), MARGIN_SIZE])
    if exitPos[1] > 0:
        pathPoint.append([MARGIN_SIZE, exitPos[1] + int(exitSize[1] / 2)])
    if exitPos[2] > 0:
        pathPoint.append([exitPos[2] + int(exitSize[2] / 2), height - (MARGIN_SIZE)])
    if exitPos[3] > 0:
        pathPoint.append([width - (MARGIN_SIZE), exitPos[3] + int(exitSize[3] / 2)])

    # Create buildings or features that should spawn a path point


    # Draw the path with the path points
    for i, point in enumerate(pathPoint):
        dir = rand.randint(0, 1)
        while (point[0] != pathPointCenter[0]) or (point[1] != pathPointCenter[1]):
            if(abs(pathPointCenter[dir] - point[dir]) >= 16):
                len = rand.randint(8, abs(pathPointCenter[dir] - point[dir]))
            else:
                len = abs(pathPointCenter[dir] - point[dir])
            xy = [point[0], point[1]]
            xy2 = xy
            if(pathPointCenter[dir] < point[dir]):
                len = -len
            xy2[dir] += len 
            point[dir] += len
            if(draw_line(2, xy[0], xy[1], xy2[0], xy2[1])):
                point = pathPointCenter
            dir ^= 1


    # Draw
    for y in range(height):
        for x in range(width):
            buffer[x, y] = color[mapData[(y * width) + x]]

    # Main loop
    done = 0
    while not done:
        pygame.transform.scale(s, WINSIZESCALE, s2)
        screen.blit(s2,(0,0))
        pygame.display.update()
        done = read_input()