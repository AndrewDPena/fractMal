#!/usr/bin/env python
"""Creates a large image out of a recolored, tiled array of itself

This program takes an image and tiles it, vertically and horizontally, and
recolors each tile to match the RGB value of the corresponding pixel from the
original image. RGB images of over 128x128 run into memory issues at the
moment.

Resources used:
How to use alpha layer and Image.composite() to add a colored overlay
https://stackoverflow.com/a/9208256
"""

from PIL import Image
Image.MAX_IMAGE_PIXELS = None

__author__ = "Andrew Peña"
__credits__ = ["Andrew Peña", "Malcolm Johnson"]
__version__ = "0.2.1"
__status__ = "Prototype"

filename = input("What is the file you wish to tile?: ")
outname = input("What do you want to save the file as?: ")
if not (".bmp" in outname or ".png" in outname or ".jpg" in outname):
    outname += ".png"
im = Image.open(filename)
gray = im.copy().convert("L")
mask = Image.new("RGBA", im.size, (0,0,0,123))
newIm = Image.new("RGB", (im.width**2, im.height**2))
row = col = 0
while row < im.height:
    while col < im.width:
        color = Image.new("RGB", im.size, im.getpixel((col, row)))
        comp = Image.composite(gray, color, mask).convert("RGB")
        newIm.paste(comp, (im.width * col, im.height * row))
        col += 1
    row += 1
    col = 0
newIm.save(outname)
