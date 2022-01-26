# plotting.py
#
# This module provides some useful functionality for plotting
import colorsys

def scale_luminosity(rgb, luminosity):
    '''Scale the given RGB color based upon the luminosity value provided'''
    if type(rgb) is str:
        rgb = rgb.lstrip('#')
        h, l, s = colorsys.rgb_to_hls(*tuple(int(rgb[i:i+2], 16)/255 for i in (0, 2, 4)))
    elif type(rgb) is tuple:
        h, l, s = colorsys.rgb_to_hls(*rgb)
    else:
        raise TypeError("Expected {}, got {}".format(str, type(rgb)))
    return colorsys.hls_to_rgb(h, min(1, l * luminosity), s)