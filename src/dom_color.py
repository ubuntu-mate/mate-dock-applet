#!/usr/bin/env python3
""" Calculate the average color of an image

    Code adapted from from: https://github.com/ZeevG/python-dominant-image-colour
"""

import binascii
import struct

try:
    import Image, ImageDraw
except ImportError:
    from PIL import Image, ImageDraw

def get_dom_color(filename):
    image = Image.open(filename)
    image = image.resize((150, 150))      # optional, to reduce time

    colour_tuple = [None, None, None]
    for channel in range(3):
        # Get data for one channel at a time

        # in case of errors stop processing and return black as the
        # dominant colour
        try:
            pixels = image.getdata(band=channel)
        except ValueError:
            return "000000"

        values = []
        for pixel in pixels:
            values.append(pixel)

        colour_tuple[channel] = int(sum(values) / len(values))

    colour = binascii.hexlify(struct.pack('BBB', *colour_tuple)).decode('utf-8')
    return colour
