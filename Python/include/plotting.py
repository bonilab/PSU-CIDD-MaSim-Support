# plotting.py
#
# This module provides some useful functionality for plotting
import colorsys


def format_ticks(yticks):
    '''Given a list of numeric tick values, round them to the nearest thousands or millions.
    
    Returns a tuple with the the list of rounded values and the formatted strings. If nothing
    was done then None is returned in both places.
    '''

    # Determine the divisor and postfix to use
    if max(yticks) > 999999:
        divisor, postfix = 1000000, 'M'
    elif max(yticks) > 999:
        divisor, postfix = 1000, 'K'
    else:
        return None, None

    # Extract the ticks and format them
    values, ticks = [], []
    for tick in yticks:
        if tick > 0:
            ticks.append('{:.1f}{}'.format(tick / divisor, postfix))
            values.append(tick)

    # Return the formatted ticks
    return values, ticks


def increment(row, col, columns):
    '''Move the current row, column to the next location (left to right) or move to the first location in the next row (top to bottom).
    
    Returns a tuple with the row as the first entry, column as the second entry.'''
    col += 1
    if col % columns == 0:
        row += 1
        col = 0
    return row, col


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