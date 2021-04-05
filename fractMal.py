#!/usr/bin/env python
"""Creates a large image out of a recolored, tiled array of itself

This program takes an image and tiles it, vertically and horizontally, and
recolors each tile to match the RGB value of the corresponding pixel from the
original image. RGB images of over 128x128 run into memory issues at the
moment.

Recent Changes:
- Version 0.9.9: Figured out how to add optional params as a dictionary, only
    needs a single save branch now
- Version 0.9.7: It now potentially works correctly when doing gifs across a
    transparent background.
- Version 0.9.5: Now uses a if elif else branch to save only a single gif.

Resources used:
How to use alpha layer and Image.composite() to add a colored overlay
https://stackoverflow.com/a/9208256
"""

import os
from PIL import Image, ImageSequence
from tkinter import Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import askyesno, showinfo, showwarning

Image.MAX_IMAGE_PIXELS = None

__author__ = "Andrew Peña"
__credits__ = ["Andrew Peña", "Malcolm Johnson"]
__version__ = "0.9.9"
__status__ = "Alpha"

class FractMal:
    def __init__(self):
        self.extensions = ['.gif', '.jpg', '.png', '.bmp']
        self.fullname = ""
        self.outname = ""
        self.fulltile = False
        self.isTransparentGIF = False
        self.transparencyXY = (0, 0)

    def __sanitize(self, imagedata):
        """Sanitizes the transparent pixels from grayscale+alpha image getdata.

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

    def __userInput(self):
        """Gets all user input at once.

        This function opens a series of dialog windows to get the file that the
        user wants to tile, the filename/location they want to save it as, and
        whether or not they want the image tiling to include the transparent
        pixels.
        """
        Tk().withdraw()
        self.filename = askopenfilename()
        self.outname = asksaveasfilename()
        if not self.filename or not self.outname:
            return False
        self.fulltile = askyesno('Fulltile', "Do you want transparent tiles to show the image too?")
        if not any(extension in self.outname for extension in self.extensions):
            self.outname += ".png" # Gives a default filetype of .png
        return True

    def __saveOut(self, frames):
        """Saves the given list as an image.

        Frames should be a list of at least one image. If it is a single image,
        the save function simply saves a single frame. If it is a gif, it has
        to compile a lot of extra info, and must handle transparency as an
        optional parameter if it was ever encountered during image tiling.
        """
        if len(frames) == 1:
            frames[0].save(self.outname)
        else:
            # tpLoc and the transparency dict entry handled here
            params = {'fp': self.outname, 'save_all': True, 'optimize': True,
            'append_images':frames[1:], 'background':self.im.info['background'],
            'duration': self.im.info['duration'], 'loop': 0, 'disposal': 2}
            if self.isTransparentGIF:
                tpLoc = frames[0].convert("P").getpixel(self.transparencyXY)
                params['transparency'] = tpLoc
            frames[0].save(**params)
        if os.path.exists(self.outname):
            showinfo("Success", "Your file was successfully tiled.")
        else:
            showwarning("Failure", "Something went wrong, sorry.")

    def tile(self):
        """Performs tiling of an image based off of user input.

        This function goes through the motions to take an image, built a new
        image of appropriate size, and tile the original image into the new one.
        A 'pixel' in the new image is a full copy of the original image.
        Each 'pixel' tile is colored the same color as the corresponding pixel
        from the original image.
        This method finishes by saving the new image in an appropriate spot.
        """
        if not self.__userInput():
            showwarning("Failue", "Something went wrong.")
            return
        self.im = Image.open(self.filename)
        # Changing the mask alpha changes output. Lower alpha, more color but less gif
        # clarity in the tiles.
        mask = Image.new("RGBA", self.im.size, (0,0,0,50))
        previousFrame = ImageSequence.Iterator(self.im)[0].convert("RGBA")
        frames = []
        if not self.fulltile:
            replacementTile = Image.new("RGBA", previousFrame.size, (0,0,0,0))
        for frame in ImageSequence.Iterator(self.im):
            newIm = Image.new("RGBA", (self.im.width**2, self.im.height**2), (0,0,0,0))
            row = col = 0
            # These are now unnecessary. Maybe Pillow updated? Or...?
            # previousFrame.alpha_composite(frame.convert("RGBA"))
            # previousFrame = frame.convert("RGBA") # This doesn't work
            grayTile = frame.convert("LA")
            grayTile.putdata(self.__sanitize(grayTile.getdata()))
            while row < frame.height:
                while col < frame.width:
                    gray = grayTile
                    pixelRGBA = frame.convert("RGBA").getpixel((col, row))
                    if ((pixelRGBA[3] == 0)):
                        if not self.isTransparentGIF:
                            self.isTransparentGIF = True
                            self.transparencyXY = (col, row)
                        pixelRGBA = (0,0,0,0)
                        if not self.fulltile:
                            gray = replacementTile
                    color = Image.new("RGBA", frame.size, pixelRGBA)
                    comp = Image.composite(gray, color, mask).convert("RGBA")
                    newIm.paste(comp, (self.im.width * col, self.im.height * row))
                    col += 1
                row += 1
                col = 0
            # Un-comment the next line to have access to each individual frame
            # newIm.save("Frame" + str(frame.tell()+1) + ".png")
            frames.append(newIm)
        self.__saveOut(frames)


if __name__ == "__main__":
    bigTile = FractMal()
    while True:
        bigTile.tile()
        if not askyesno("Continue?", "Do you wish to tile another image?"):
            break
