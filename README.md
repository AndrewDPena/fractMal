# FractMal
## An image tiling program

# About the Project
FractMal is a silly program written on a whim. The idea is to take an input image, and tile it in proportion to its pixels. For example, a 32 x 32 image becomes a 32<sup>2</sup> x  32<sup>2</sup>  image, creating a sort of collage wherein each "pixel" of the new image is a full copy of the original, and each "pixel" in the new image has a colored layer matching the color of the corresponding pixel in the original image.

This project works really well on still images, and decently well on gifs. There are minor color issues frame-to-frame in gifs, but this isn't a major concern at this time.

# How to use
## Through command window
Simply navigate to the directory containing the file, and run:
```
python fractMal.py
```
You may need to use pip to install Pillow. From there, the program should run automatically, using dialog boxes to ask you to open an image, choose a save location/name, and whether or not you want to do a full tile.

## Using the .exe
I am including a .exe as a sort of practice run on pyinstaller. You *should* be able to simply run the executable and get the same functionality. It may run via your anti-virus at first, loading everything slowly and not quite running correctly (this is what happened to me). Simply go through the dialog boxes until you actually get it to run correctly, and it should be fine.

**Note: This may only work on Windows 64-bit platforms.**

# Known Issues
* The .exe file crashes if you save as a filename without explicitly naming the extension, rather than safely defaulting to a .png
* The .exe doesn't correctly expand params in the save method, leading to a transparency bug on gifs with no transparency.

# Author
Andrew Peña andrewdpena@gmail.com