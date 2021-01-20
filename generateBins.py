#!/usr/bin/python

# generateBins.py
#
# This script generates the bins that need to be run to determine the beta values

#import os
#from Scripts.Calibration.include.ascFile import *
import head as hd
from pathlib import Path


# Define the major influences of the beta values
PFPR_FILE       = Path("../../GIS/rwa_pfpr2to10.asc")
POPULATION_FILE = Path("../../GIS/rwa_population.asc")

# TODO Determine how to do this computationally
# Reference values for Rwanda
#ZONE = 0
#TREATMENT = 0.56

TREATMENT = input("ENTER Treatment rate:")
ZONE = input("Enter Zone Value:")

# TODO Determine the bins computationally
# Following bins are for Rwanda
populationBins = [2125, 5640, 8989, 12108, 15577, 20289, 27629, 49378, 95262, 286928]


def getBin(value, bins):
    bins.sort()
    for item in bins:
        if value < item: return item
    if item >= max(bins):
        return max(bins)


def process():
    # Load the relevent data
    [ ascHeader, pfpr ] = hd.load_asc(PFPR_FILE)
    [ ascHeader, population ] = hd.load_asc(POPULATION_FILE)

    # Prepare our results
    ranges = {}

    # Process the data
    for row in range(0, ascHeader['nrows']):
        for col in range(0, ascHeader['ncols']):

            # Press on if there is nothing to do
            if population[row][col] == ascHeader['nodata']: continue

            # Get the bin
            popBin = getBin(population[row][col], populationBins)

            # Add to the dictionary as needed
            if popBin not in ranges: ranges[popBin] = []
            
            # Add to our data sets
            ranges[popBin].append(pfpr[row][col])

    return [ ranges ]


def save(ranges, filename, username):
    with open(filename, 'w') as script:
        # Print the front matter
        script.write("#!/bin/bash\n\n")
        script.write("source ./calibrationLib.sh\n")
        value = " ".join([str(x) for x in sorted(populationBins)])
        script.write("generateAsc \"\\\"{}\\\"\"\n".format(value))
        script.write("run {} \"\\\"{}\\\"\" \"\\\"{}\\\"\" {}".format(ZONE, value, TREATMENT, username))



if __name__ == '__main__':
    if len(hd.sys.argv) != 2:
        print ("Usage: ./generateBins.py [username]")
        print ("username - the user who will be running the calibration on the cluster")
        exit(0)

    # Parse the parameters
    username = str(hd.sys.argv[1])

    # Process and print the relevent ranges for the user
    [ ranges ] = process()
    for population in sorted(ranges):
        print ("{} - {} to {} PfPR".format(population, min(ranges[population]), max(ranges[population])))

    # Save the basic script
    if not hd.os.path.isdir('out'): hd.os.mkdir('out')
    save(ranges, 'out/calibration.sh', username)
