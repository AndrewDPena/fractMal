#!/usr/bin/env python
"""Creates a large image out of a recolored, tiled array of itself

This program takes an image and tiles it, vertically and horizontally, and
recolors each tile to match the RGB value of the corresponding pixel from the
original image. RGB images of over 128x128 run into memory issues at the
moment.

Current Issues:
- Works poorly on gifs with movement across a transparent background, since it
simply pastes each frame over the previous frame

Resources used:
How to use alpha layer and Image.composite() to add a colored overlay
https://stackoverflow.com/a/9208256
"""

from PIL import Image, ImageSequence
Image.MAX_IMAGE_PIXELS = None

__author__ = "Andrew Peña"
__credits__ = ["Andrew Peña", "Malcolm Johnson"]
__version__ = "0.7.0"
__status__ = "Prototype"

filename = input("What is the file you wish to tile?: ")
outname = input("What do you want to save the file as?: ")
fulltile = input("Enter 'y' if you want a full tile: ").lower()
if not (".gif" in outname or ".bmp" in outname or ".png" in outname
or ".jpg" in outname): # Gives a default filetype of .png
    outname += ".png"
im = Image.open(filename)
# Changing the mask alpha changes output. Lower alpha, more color but less gif
# clarity in the tiles.
mask = Image.new("RGBA", im.size, (0,0,0,50))
previousFrame = ImageSequence.Iterator(im)[0].convert("RGBA")
frames = []
# Possibly unnecessary, this is used to distinguish between gifs with and
# without transparency, which matters during the save process mostly. The XY
# is used to locate the transparent pixel in the palette.
isTransparentGIF = False
transparencyXY = (0, 0)
for frame in ImageSequence.Iterator(im):
    newIm = Image.new("RGBA", (im.width**2, im.height**2), (0,0,0,0))
    row = col = 0
    # alpha_composite allows partial/additive gifs to work, but breaks gifs
    # with motion over a transparent background. This needs to be re-thought.
    previousFrame.alpha_composite(frame.convert("RGBA"))
    # previousFrame = frame.convert("RGBA") # This doesn't work
    if fulltile == 'y':
        grayT = previousFrame.convert("LA")
    else:
        grayT = Image.new("RGBA", (previousFrame.size), (0,0,0,0))
    grayF = previousFrame.convert("L")
    while row < frame.height:
        while col < frame.width:
            pixelRGBA = previousFrame.getpixel((col, row))
            if ((pixelRGBA[3] == 0)):
                if not isTransparentGIF:
                    isTransparentGIF = True
                    transparencyXY = (col, row)
                gray = grayT
                pixelRGBA = (0,0,0,0)
            else:
                gray = grayF
            color = Image.new("RGBA", frame.size, pixelRGBA)
            comp = Image.composite(gray, color, mask).convert("RGBA")
            newIm.paste(comp, (im.width * col, im.height * row))
            col += 1
        row += 1
        col = 0
    # Un-comment the next line to have access to each individual frame
    # newIm.save("Frame" + str(frame.tell()+1) + ".png")
    frames.append(newIm)
if len(frames) == 1:
    frames[0].save(outname)
else:
    frames[0].save(outname, save_all = True, optimize=True,
    append_images=frames[1:], backgound=im.info['background'],
    duration = im.info['duration'], loop=0)
    if isTransparentGIF:
        tpLoc = frames[0].convert("P").getpixel(transparencyXY)
        temp = Image.open(outname)
        temp.info['transparency'] = tpLoc
        temp.save("new" + outname, save_all=True)
