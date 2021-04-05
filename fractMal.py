#!/usr/bin/env python
"""Creates a large image out of a recolored, tiled array of itself

This program takes an image and tiles it, vertically and horizontally, and
recolors each tile to match the RGB value of the corresponding pixel from the
original image. RGB images of over 128x128 run into memory issues at the
moment.

Current Issues:
- Works poorly on gifs with movement across a transparent background, since it
simply pastes each frame over the previous frame

- Saves two files for transparent gifs, Pillow's image library seems resistant
to saving in place.

Resources used:
How to use alpha layer and Image.composite() to add a colored overlay
https://stackoverflow.com/a/9208256
"""

from PIL import Image, ImageSequence
from tkinter import Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import askyesno

Image.MAX_IMAGE_PIXELS = None

__author__ = "Andrew Peña"
__credits__ = ["Andrew Peña", "Malcolm Johnson"]
__version__ = "0.9.2"
__status__ = "Prototype"

class FractMal:
    def __init__(self):
        self.extensions = ['.gif', '.jpg', '.png', '.bmp']
        self.fullname = ""
        self.outname = ""
        self.fulltile = False

    def sanitize(self, imagedata):
        """Sanitizes the transparent pixels from grayscale+alpha image getdata

        Given image data from an Image in "LA" mode, this function scrubs each
        pixel of invisible color data. This is necessary since PNG has a bad habit
        of not caring about the RGB values for a pixel with an alpha of 0, and that
        interferes with the method being used to overlay colors in this program.
        """
        cleandata = []
        for pixel in imagedata:
            if pixel[1] == 0:
                newPixel = (0,0)
            else:
                newPixel = pixel
            cleandata.append(newPixel)
        return cleandata

    def userInput(self):
        Tk().withdraw()
        self.filename = askopenfilename()
        self.outname = asksaveasfilename()
        self.fulltile = askyesno('Fulltile', "Do you want transparent tiles to show the image too?")
        if not any(extension in self.outname for extension in self.extensions):
            self.outname += ".png" # Gives a default filetype of .png

    def tile(self):
        im = Image.open(self.filename)
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
            if not self.fulltile:
                replacementTile = Image.new("RGBA", previousFrame.size, (0,0,0,0))
            grayTile = previousFrame.convert("LA")
            grayTile.putdata(self.sanitize(grayTile.getdata()))
            while row < frame.height:
                while col < frame.width:
                    gray = grayTile
                    pixelRGBA = previousFrame.getpixel((col, row))
                    if ((pixelRGBA[3] == 0)):
                        if not isTransparentGIF:
                            isTransparentGIF = True
                            transparencyXY = (col, row)
                        pixelRGBA = (0,0,0,0)
                        if not self.fulltile:
                            gray = replacementTile
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
            frames[0].save(self.outname)
        else:
            frames[0].save(self.outname, save_all = True, optimize=True,
            append_images=frames[1:], backgound=im.info['background'],
            duration = im.info['duration'], loop=0)
            if isTransparentGIF:
                tpLoc = frames[0].convert("P").getpixel(transparencyXY)
                temp = Image.open(self.outname)
                temp.info['transparency'] = tpLoc
                temp.save("new" + self.outname, save_all=True)

if __name__ == "__main__":
    tiler = FractMal()
    tiler.userInput()
    tiler.tile()
