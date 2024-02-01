# ascFile.py
#
# This module contains some common functions for working with ASC files.
import sys


# Compare the two header files, return True if they are the same, False otherwise.
# If printError is set, then errors will be printed to stderr
def compare_header(one, two, printError=True):
    result = True
    if one['ncols'] != two['ncols']:
        if printError:
            sys.stderr.write('{} != {} ncols\n'.format(one['ncols'], two['ncols']))
        result = False
    if one['nrows'] != two['nrows']:
        if printError:
            sys.stderr.write('{} != {} nrows\n'.format(one['nrows'], two['nrows']))
        result = False
    if one['xllcorner'] != two['xllcorner']:
        if printError:
            sys.stderr.write('{} != {} xllcorner\n'.format(one['xllcorner'], two['xllcorner']))
        result = False
    if one['yllcorner'] != two['yllcorner']:
        if printError:
            sys.stderr.write('{} != {} yllcorner\n'.format(one['yllcorner'], two['yllcorner']))
        result = False
    if one['cellsize'] != two['cellsize']:
        if printError:
            sys.stderr.write('{} != {} cellsize\n'.format(one['cellsize'], two['cellsize']))
        result = False
    if one['nodata'] != two['nodata']:
        if printError:
            sys.stderr.write('{} != {} nodata\n'.format(one['nodata'], two['nodata']))
        result = False
    return result


# Compare the two data sections, return True if they are the same, False otherwise.
# If printError is set, then errors will be printed to stderr
def compare_data(one, two, nodata, printError=True, errorLimit=-1):
    result = True
    count = 0
    for row in range(0, len(one)):
        for col in range(0, len(one[row])):
            # Set the values
            a = one[row][col]
            b = two[row][col]

            # Are they both nodata
            if (a == nodata and a != b) or (b == nodata and a != b):
                result = False
                count += 1
                if printError:
                    if errorLimit == -1 or count < errorLimit:
                        sys.stderr.write('Mismatched nodata at {}, {}\n'.format(row, col))
                        sys.stderr.write('One: {}, Two {}\n'.format(a, b))

    if errorLimit != -1 and count > errorLimit:
        sys.stderr.write('Plus {} additional errors\n'.format(count - errorLimit))
    return result


# Generate an ASC header with values zeroed
def get_header():
    header = {}
    header['ncols'] = 0
    header['nrows'] = 0
    header['xllcorner'] = 0
    header['yllcorner'] = 0
    header['cellsize'] = 0
    header['nodata'] = 0
    return header


# Read the ASC file and return the header / data
def load_asc(filename):
    with open(filename) as input:
        lines = input.readlines()

        # Read the header values
        header = {}
        header['ncols'] = int(lines[0].split()[1])
        header['nrows'] = int(lines[1].split()[1])
        header['xllcorner'] = float(lines[2].split()[1])
        header['yllcorner'] = float(lines[3].split()[1])
        header['cellsize'] = float(lines[4].split()[1])
        header['nodata'] = int(lines[5].split()[1])

        # Read the rest of the entries
        data = []
        for ndx in range(6, header['nrows'] + 6):
            row = [float(value) for value in lines[ndx].split()]
            data.append(row)

        return header, data


# Write an ASC file using the data provided
def write_asc(header, data, filename):
    with open(filename, 'w') as output:

        # Write the header values
        output.write('ncols         ' + str(header['ncols']) + '\n')
        output.write('nrows         ' + str(header['nrows']) + '\n')
        output.write('xllcorner     ' + str(header['xllcorner']) + '\n')
        output.write('yllcorner     ' + str(header['yllcorner']) + '\n')
        output.write('cellsize      ' + '{0:.8g}'.format(header['cellsize']) + '\n')
        output.write('NODATA_value  ' + str(header['nodata']) + '\n')

        # Write the data
        for ndx in range(0, header['nrows']):
            row = ['{0:.8g}'.format(value) for value in data[ndx]]
            row = ' '.join(row)
            output.write(row)
            output.write('\n')
