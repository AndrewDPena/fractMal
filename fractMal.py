__author__ = "Andrew Peña"
__credits__ = ["Andrew Peña", "Malcolm Johnson"]
__version__ = "0.1.0"
__status__ = "Prototype"
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS = None

"""This program takes an image and tiles it, vertically and horizontally, and
adds a colored line to the bottom of each row of images. It also crops the top
and the left side of the image in order to fit certain software.
Currently, these values must be hard-coded; that is, user input is not accepted
after the script has been run.

Parameters:
newImMultH -- The number of tiles, vertically. Do NOT set below 1.
newImMultW -- The number of tiles, horizontally. Do NOT set below 1.
"""

im = Image.open("64square.jpg")
bw = im.copy().convert("L")
mask = Image.new("RGBA", im.size, (0,0,0,123))
newIm = Image.new("RGB", (im.width**2, im.height**2))
r = 0
c = 0
while r < im.height:
    while c < im.width:
        color = Image.new("RGB", im.size, im.getpixel((c, r)))
        comp = Image.composite(bw, color, mask).convert("RGB")
        newIm.paste(comp, (im.width * c, im.height * r))
        c += 1
    r += 1
    c = 0
newIm.save("64output.png")
