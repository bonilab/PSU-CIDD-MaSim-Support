# validate_raster.py
#
# This script is intended to validate raster files to ensure they are aligned correctly.
import os

from include.ascFile import *

PATH = '../../GIS'


def compare(one, two):
    # Load the ASC files
    [ oneHeader, oneValues ] = load_asc(one)
    [ twoHeader, twoValues ] = load_asc(two)

    # Check the files
    result = True
    result = result and compare_header(oneHeader, twoHeader)
    result = result and compare_data(oneValues, twoValues, oneHeader['nodata'])
    return result


def main():
    first = ''
    error = False
    for filename in next(os.walk(PATH))[2]:
        # Continue if we this is not an ASC
        if ".asc" not in filename: continue

        # If the first one has not been set, do so and continue
        if first == '':
            first = os.path.join(PATH, filename)
            continue

        # We now have two paths, so compare the first versus the new one
        second = os.path.join(PATH, filename)
        if not compare(first, second):
            error = True
            print 'Error with alignment between {} and {}'.format(first, second)
    
    if not error:
        print 'Complete! No errors.'


if __name__ == '__main__':
    main()