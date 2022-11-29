#!/usr/bin/python3

# createVerificationReference.py
#
# This module reads the relevant ASC files for a projection to generate the 
# weighted PfPR file that is used to check the model calibration.
import argparse
import glob
import os
import re
import sys

# Import our libraries
sys.path.append(os.path.join(os.path.dirname(__file__), 'include'))

import include.standards as std
from include.ascFile import load_asc


# Filename template to use for the results
TEMPLATE = "{}-weighted_pfpr.csv"


def main(gis):
    # Get the prefix and open the ASC files
    prefix = scan_prefix(gis)
    [header, districts] = load_asc(os.path.join(gis, std.DISTRICT_FILE.format(prefix)))
    [_, pfpr] = load_asc(os.path.join(gis, std.PFPR_FILE.format(prefix)))
    [_, population] = load_asc(os.path.join(gis, std.POPULATION_FILE.format(prefix)))
    
    # Iterate through the district file to guide the calculation
    data = {}
    for row in range(0, header['nrows']):
        for col in range(0, header['ncols']):

            # Continue on no data
            if districts[row][col] == header['nodata']:
                continue

            # Prepare our dictionary as needed
            district = int(districts[row][col])
            if district not in data:
                data[district] = [0, 0]

            # First value is the weighted PfPR sum
            data[district][0] += ((pfpr[row][col] * population[row][col]) * 100.0)

            # Second value is the population sum
            data[district][1] += population[row][col]

    # Generate the results file
    filename = TEMPLATE.format(prefix)
    with open(filename, 'w') as csvfile:
        for district in sorted(data.keys()):
            csvfile.write("{},{}\n".format(district, round(data[district][0] / data[district][1], 2)))
    print("{} created".format(filename))        


# Scan the directory provided, based upon the file extension given, to determine if 
# there is a common prefix. For conforming projects, they should all have the same
# country code.
def scan_prefix(directory):
    prefix = None
    for file in glob.glob(os.path.join(directory, "*.asc")):
        match = re.search(r"^.*\/([a-z]{3})[-_].*\.asc", file)
        if match is None: 
            continue
        if prefix is None: 
            prefix = match.group(1)
        if prefix != match.group(1):
            raise Exception("More than one possible prefix found in GIS directory: {}, {}".format(prefix, match.group(1)))
    return prefix            


if __name__ == '__main__':
    # Prase the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', action='store', dest='gis', required=True,
        help='The path to the directory that the GIS files can be found in')
    args = parser.parse_args()

    # Call the main function with the paramters
    try:
        main(args.gis)
    except Exception as err:
        sys.stderr.write("Error: {}\n".format(str(err)))
        sys.exit(1)