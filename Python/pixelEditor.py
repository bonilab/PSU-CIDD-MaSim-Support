#!/usr/bin/python3

# pixelEditor.py
#
# This script takes an ASC filename, x, y, and pixel value as an input. The 
# file is then opened and the pixel at that location is updated to be the value
# and saved.
import os
import sys

# Import our libraries
sys.path.append(os.path.join(os.path.dirname(__file__), "include"))
import include.ascFile as asc


def main(filename, row, col, value):
    # Load the ASC file
    header, data = asc.load_asc(filename)

    # Edit the value
    data[row][col] = value

    # Write the ASC file
    asc.write_asc(header, data, filename)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: ./pixelEditor.py [filename] [row] [col] [value]")
        print("Coordinates are assumed to be zero indexed and the file specified will be updated following execution")
        exit(0)

    # Parse the parameters
    filename = str(sys.argv[1])
    row = int(sys.argv[2])
    col = int(sys.argv[3])
    value = float(sys.argv[4])

    main(filename, row, col, value)