#!/usr/bin/env python
"""Creates a large image out of a recolored, tiled array of itself

This program takes an image and tiles it, vertically and horizontally, and
recolors each tile to match the RGB value of the corresponding pixel from the
original image. RGB images of over 128x128 run into memory issues at the
moment.

Current Issues:
- Works poorly on gifs with movement across a transparent background, since it
simply pastes each frame over the previous frame

- That save function looks like garbage. There should be a way to have one save
function for gifs where transparent is only passed as a parameter if
isTransparent is true

Resources used:
How to use alpha layer and Image.composite() to add a colored overlay
https://stackoverflow.com/a/9208256
"""

from PIL import Image, ImageSequence
Image.MAX_IMAGE_PIXELS = None

__author__ = "Andrew Peña"
__credits__ = ["Andrew Peña", "Malcolm Johnson"]
__version__ = "0.6.0"
__status__ = "Prototype"

filename = input("What is the file you wish to tile?: ")
outname = input("What do you want to save the file as?: ")
if not (".gif" in outname or ".bmp" in outname or ".png" in outname
or ".jpg" in outname):
    outname += ".png"
im = Image.open(filename)
mask = Image.new("RGBA", im.size, (0,0,0,123))
previousFrame = ImageSequence.Iterator(im)[0].convert("RGBA")
frames = []
isTransparent = False
transparencyXY = (0, 0)
for frame in ImageSequence.Iterator(im):
    newIm = Image.new("RGBA", (im.width**2, im.height**2), (0,0,0,0))
    row = col = 0
    previousFrame.alpha_composite(frame.convert("RGBA"))
    grayT = previousFrame.convert("LA")
    grayF = previousFrame.convert("L")
    while row < frame.height:
        while col < frame.width:
            prevRGBA = previousFrame.getpixel((col, row))
            gray = grayF
            if ((prevRGBA[3] == 0)):
                if not isTransparent:
                    isTransparent = True
                    transparencyXY = (col, row)
                gray = grayT
                prevRGBA = (75, 75, 75, 0)
            color = Image.new("RGBA", frame.size, prevRGBA)
            comp = Image.composite(gray, color, mask).convert("RGBA")
            newIm.paste(comp, (im.width * col, im.height * row))
            col += 1
        row += 1
        col = 0
    frames.append(newIm)
if len(frames) == 1:
    frames[0].save(outname)
else:
    if isTransparent:
        tpLoc = frames[0].convert("P").getpixel(transparencyXY)
        frames[0].save(outname, save_all=True, optimize=True,
        append_images=frames[1:], backgound=im.info['background'],
        transparency=tpLoc, duration = im.info['duration'],
        loop=0)
    else:
        frames[0].save(outname, save_all=True, optimize=True,
        append_images=frames[1:], backgound=im.info['background'],
        duration = im.info['duration'], loop=0)
