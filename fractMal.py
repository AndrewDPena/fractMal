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
        self.working_image = None
        self.extensions = ['.gif', '.jpg', '.png', '.bmp']
        self.fullname = ""
        self.output_name = ""
        self.full_tile = False

    @staticmethod
    def __sanitize(imagedata):
        """Sanitizes the transparent pixels from grayscale+alpha image getdata.

        Given image data from an Image in "LA" mode, this function scrubs each
        pixel of invisible color data. This is necessary since PNG has a bad habit
        of not caring about the RGB values for a pixel with an alpha of 0, and that
        interferes with the method being used to overlay colors in this program.
        """
        cleandata = []
        for pixel in imagedata:
            if pixel[1] == 0:
                new_pixel = (0, 0)
            else:
                new_pixel = pixel
            cleandata.append(new_pixel)
        return cleandata

    def __user_input(self):
        """Gets all user input at once.

        This function opens a series of dialog windows to get the file that the
        user wants to tile, the filename/location they want to save it as, and
        whether they want the image tiling to include the transparent
        pixels.
        """
        Tk().withdraw()
        self.filename = askopenfilename()
        self.output_name = asksaveasfilename()
        if not self.filename or not self.output_name:
            return False
        self.full_tile = askyesno('Full tile', "Do you want transparent tiles to show the image too?")
        if not any(extension in self.output_name for extension in self.extensions):
            self.output_name += ".png"  # Gives a default filetype of .png
        return True

    def __save_out(self, frames):
        """Saves the given list as an image.

        Frames should be a list of at least one image. If it is a single image,
        the save function simply saves a single frame. If it is a gif, it has
        to compile a lot of extra info, and must handle transparency as an
        optional parameter if it was ever encountered during image tiling.
        """
        if len(frames) == 1:
            frames[0].save(self.output_name)
        else:
            # tp_loc and the transparency dict entry handled here
            params = {'fp': self.output_name, 'save_all': True, 'optimize': True,
                      'append_images': frames[1:], 'background': self.working_image.info['background'],
                      'duration': self.working_image.info['duration'], 'loop': 0, 'disposal': 2,
                      'include_color_table': True}
            frames[0].save(**params)
        if os.path.exists(self.output_name):
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
        if not self.__user_input():
            showwarning("Failure", "Something went wrong.")
            return
        self.working_image = Image.open(self.filename)
        # Changing the mask alpha changes output. Lower alpha, more color but less gif
        # clarity in the tiles.
        mask = Image.new("RGBA", self.working_image.size, (0, 0, 0, 50))
        previous_frame = ImageSequence.Iterator(self.working_image)[0].convert("RGBA")
        frames = []
        # replacement_tile is a blank tile to replace all transparent tiles
        replacement_tile = Image.new("RGBA", previous_frame.size, (0, 0, 0, 0))
        for frame in ImageSequence.Iterator(self.working_image):
            new_im = Image.new("RGBA", (self.working_image.width ** 2, self.working_image.height ** 2), (0, 0, 0, 0))
            row = col = 0
            # These are now unnecessary. Maybe Pillow updated? Or...?
            # previous_frame.alpha_composite(frame.convert("RGBA"))
            # previous_frame = frame.convert("RGBA") # This doesn't work
            gray_tile = frame.convert("LA")
            gray_tile.putdata(self.__sanitize(gray_tile.getdata()))
            while row < frame.height:
                while col < frame.width:
                    gray = gray_tile
                    pixel_rgba = frame.convert("RGBA").getpixel((col, row))
                    if pixel_rgba[3] == 0:
                        pixel_rgba = (0, 0, 0, 0)
                        if not self.full_tile:
                            gray = replacement_tile
                    color = Image.new("RGBA", frame.size, pixel_rgba)
                    comp = Image.composite(gray, color, mask).convert("RGBA")
                    new_im.paste(comp, (self.working_image.width * col, self.working_image.height * row))
                    col += 1
                row += 1
                col = 0
            # Un-comment the next line to have access to each individual frame
            # new_im.save("Frame" + str(frame.tell()+1) + ".png")
            frames.append(new_im)
        self.__save_out(frames)


if __name__ == "__main__":
    bigTile = FractMal()
    while True:
        bigTile.tile()
        if not askyesno("Continue?", "Do you wish to tile another image?"):
            break
