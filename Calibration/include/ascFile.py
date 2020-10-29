# ascFile.py
# 
# This module contains some common functions for working with ASC files.
import sys

# Compare the two header files, return True if they are the same, False otherwise. 
# If printError is set, then errors will be printed to stderr
def compare_header(one, two, printError = True):
    result = True
    if one['ncols'] != two['ncols']:
        if printError: sys.stderr.write('{} != {} ncols\n'.format(one['ncols'], two['ncols']))
        result = False
    if one['nrows'] != two['nrows']:
        if printError: sys.stderr.write('{} != {} nrows\n'.format(one['nrows'], two['nrows']))
        result = False
    if one['xllcorner'] != two['xllcorner']:
        if printError: sys.stderr.write('{} != {} xllcorner\n'.format(one['xllcorner'], two['xllcorner']))
        result = False
    if one['yllcorner'] != two['yllcorner']:
        if printError: sys.stderr.write('{} != {} yllcorner\n'.format(one['yllcorner'], two['yllcorner']))
        result = False
    if one['cellsize'] != two['cellsize']:
        if printError: sys.stderr.write('{} != {} cellsize\n'.format(one['cellsize'], two['cellsize']))
        result = False
    if one['nodata'] != two['nodata']:
        if printError: sys.stderr.write('{} != {} nodata\n'.format(one['nodata'], two['nodata']))
        result = False                                
    return result


# Compare the two data sections, return True if they are the same, False otherwise. 
# If printError is set, then errors will be printed to stderr
def compare_data(one, two, nodata, printError = True):
    result = True

    for row in range(0, len(one)):
        for col in range(0, len(one[row])):
            # Set the values
            a = one[row][col]
            b = two[row][col]

            # Are they both nodata
            if (a == nodata and a != b) or (b == nodata and a != b):
                result = False
                if printError: 
                    sys.stderr.write('Mismatched nodata at {}, {}\n'.format(row, col))
                    sys.stderr.write('One: {}, Two {}\n'.format(a, b))


    return result


# Read the ASC file and return the header / data
def load_asc(filename):
    with open(filename) as ascfile:    
        lines = ascfile.readlines()

        # Read the header values
        ascheader = {}
        ascheader['ncols'] = int(lines[0].split()[1])
        ascheader['nrows'] = int(lines[1].split()[1])
        ascheader['xllcorner'] = float(lines[2].split()[1])
        ascheader['yllcorner'] = float(lines[3].split()[1])
        ascheader['cellsize'] = float(lines[4].split()[1])
        ascheader['nodata'] = int(lines[5].split()[1])

        # Read the rest of the enteries
        ascdata = []
        for ndx in range(6, ascheader['nrows'] + 6):
            row = [ float(value) for value in lines[ndx].split() ]
            ascdata.append(row)

        return [ ascheader, ascdata ]

# Write an ASC file using the data provided
def write_asc(ascheader, ascdata, filename):
    with open(filename, 'w') as ascfile:

        # Write the header values
        ascfile.write('ncols         ' + str(ascheader['ncols']) + '\n')
        ascfile.write('nrows         ' + str(ascheader['nrows']) + '\n')
        ascfile.write('xllcorner     ' + str(ascheader['xllcorner']) + '\n')
        ascfile.write('yllcorner     ' + str(ascheader['yllcorner']) + '\n')
        ascfile.write('cellsize      ' + '{0:.8g}'.format(ascheader['cellsize']) + '\n')
        ascfile.write('NODATA_value  ' + str(ascheader['nodata']) + '\n')
                
        # Write the data
        for ndx in range(0, ascheader['nrows']):
            row = [ '{0:.8g}'.format(value) for value in ascdata[ndx] ]
            row = ' '.join(row)
            ascfile.write(row)
            ascfile.write('\n')
