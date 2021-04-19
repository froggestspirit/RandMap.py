import random as rand

#Map size
height = rand.randint(15,60) * 2
width = rand.randint(15,60) * 2
size = (height + 14) * (width + 15)
#Enforce maximum size
while size >= 0x2800:
    if height >= width:
        height -= 2;
    else:
        width -= 2;
    size = (height + 14) * (width + 15)

print(width)
print(height)

