#!/usr/bin/python3

# validate_raster.py
#
# This script is intended to validate raster files to ensure they are aligned correctly.

# Add the common include directory before importing our custom libraries

import sys
sys.path.append("include")

import os
from ascFile import *

def compare(one, two):
    # Load the ASC files
    [ oneHeader, oneValues ] = load_asc(one)
    [ twoHeader, twoValues ] = load_asc(two)

    # Check the files
    result = True
    result = result and compare_header(oneHeader, twoHeader)
    result = result and compare_data(oneValues, twoValues, oneHeader['nodata'])
    return result


def main(path):
    # Prepare the variables
    count = 0
    first = ''
    error = False

    for filename in next(os.walk(path))[2]:
        # Continue if we this is not an ASC
        if ".asc" not in filename: continue

        # If the first one has not been set, do so and continue
        if first == '':
            print("Using {} as reference".format(filename))
            first = os.path.join(path, filename)
            continue

        # We now have two paths, so compare the first versus the new one
        second = os.path.join(path, filename)
        if not compare(first, second):
            error = True
            print('Error with alignment between {} and {}'.format(first, second))

        # Update the count
        count = count + 1
    
    # Print the status
    print("{} files checked".format(count))

    if not error:
        print("No errors detected")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: ./validateRaster.py [path]")
        print("path - path to GIS files relative to this script")
        print("\nExample: ./validateRaster.py ../GIS\n")
        exit(0)

    # Parse the parameters
    path = sys.argv[1]

    # Main entry point
    main(path)