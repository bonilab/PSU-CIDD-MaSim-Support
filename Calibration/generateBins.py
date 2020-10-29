# generateBins.py
#
# This script generates the bins that need to be run to determine the beta values
import math

from include.ascFile import *

# Define the major influences of the beta values
PFPR_FILE       = '../GIS/rwa_pfpr2to10.asc'
POPULATION_FILE = '../GIS/rwa_population.asc'

# Only one treatment bin for Rwanda
treatmentBins = [ 0.99 ]

# TODO Determine the bins computationally
populationBins = [797, 1417, 2279, 3668, 6386, 12627, 25584, 53601, 117418]


def getBin(value, bins):
    bins.sort()
    for item in bins:
        if value < item: return item
    if item >= max(bins):
        return max(bins)


def process():
    # Load the relevent data
    [ ascHeader, pfpr ] = load_asc(PFPR_FILE)
    [ ascHeader, population ] = load_asc(POPULATION_FILE)

    # Prepare our results
    pfprRanges = {}

    # Process the data
    for row in range(0, ascHeader['nrows']):
        for col in range(0, ascHeader['ncols']):

            # Press on if there is nothing to do
            if population[row][col] == ascHeader['nodata']: continue

            # Get the bin
            popBin = getBin(population[row][col], populationBins)

            # Add to the dictionary as needed
            if popBin not in pfprRanges: pfprRanges[popBin] = []
            
            # Add to our data sets
            pfprRanges[popBin].append(pfpr[row][col])

    return [ pfprRanges ]


def save(pfprRanges, filename):
    with open(filename, 'w') as script:
        # Print the front matter
        script.write("#!/bin/bash\n")
        script.write("\n# Calibration template script\n")
        
        # Print the blocks for the calibration
        values = " ".join(str(value) for value in sorted(pfprRanges.keys()))
        script.write("for population in {}; do\n".format(values))
        script.write("  for beta in `seq 0.05 0.05 1.20`; do\n")
        script.write("\n#TODO\n\n")
        script.write("  done\n")
        script.write("done\n")


if __name__ == '__main__':
    # Process the data
    [ pfprRanges ] = process()

    # Print the relevent ranges for the user
    for zone in pfprRanges.keys():
        print "Populations: {}".format(sorted(pfprRanges[zone].keys()))
        for popBin in sorted(pfprRanges[zone].keys()):
            print "{} - {} to {} PfPR".format(popBin, min(pfprRanges[zone][popBin]), max(pfprRanges[zone][popBin]))
        print

    # Save the basic script
    save(pfprRanges, 'out/calibration.sh')
