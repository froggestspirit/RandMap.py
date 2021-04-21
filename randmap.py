import random as rand
import math, pygame
from pygame.locals import *

WINSIZE = [240, 240]
WINSIZESCALE = [480, 480]

def read_input():
    for e in pygame.event.get():
        if e.type == QUIT or (e.type == KEYUP and e.key == K_ESCAPE):
            return True
            break

clock = pygame.time.Clock()
#initialize and prepare screen
pygame.init()
screen = pygame.display.set_mode(WINSIZESCALE)
s = pygame.Surface((WINSIZE))  # the size of your rect
s2 = pygame.Surface((WINSIZESCALE))
white = 255, 240, 200
black = 120, 120, 140
screen.fill(black)

#Map size
width = rand.randint(15,60) * 2
height = rand.randint(15,60) * 2
size =  (width + 15) * (height + 14)
#Enforce maximum size
while size >= 0x2800:
    if height >= width:
        height -= 2;
    else:
        width -= 2;
    size = (height + 14) * (width + 15)


#Map type, exits, should be defined beforehand
MARGIN_SIZE = 7
mapType = rand.randint(0,15)
exitPos = [0, 0, 0, 0]
exitSize = [0, 0, 0, 0]
mapDim = [width, height, width, height]
bit = 1
for i in range(4):
    if mapType & bit:
        exitPos[i] = rand.randint(MARGIN_SIZE, mapDim[i] - MARGIN_SIZE)
        exitSize[i] = rand.randint(4, 8)
        if (exitPos[i] + (exitSize[i] - 1)) > (mapDim[i] - MARGIN_SIZE):
            exitPos[i] -= (exitPos[i] + (exitSize[i] - 1)) - (mapDim[i] - MARGIN_SIZE)
    bit *= 2

print(f"{width} by {height}")
mapData = ""
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
            mapData += "0"
        elif locType == 4:
            mapData += " "
        elif locType == 1:
            if (x >= exitPos[0]) and (x < exitPos[0] + (exitSize[0])):
                mapData += " "
            else:
                mapData += "0"
        elif locType == 3:
            if (y >= exitPos[1]) and (y < exitPos[1] + (exitSize[1])):
                mapData += " "
            else:
                mapData += "0"
        elif locType == 5:
            if (y >= exitPos[3]) and (y < exitPos[3] + (exitSize[3])):
                mapData += " "
            else:
                mapData += "0"
        elif locType == 7:
            if (x >= exitPos[2]) and (x < exitPos[2] + (exitSize[2])):
                mapData += " "
            else:
                mapData += "0"

for y in range(height):
    print(mapData[(y * width):((y + 1) * width)])

done = 0
while not done:
    s.fill(black)
    pygame.transform.scale(s, WINSIZESCALE, s2)
    screen.blit(s2,(0,0))
    pygame.display.update()
    done = read_input()