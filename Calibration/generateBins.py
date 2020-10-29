# generateBins.py
#
# This script generates the bins that need to be run to determine the beta values
import math

from include.ascFile import *

# TODO Prompt the user for these?
# Define the major influencer of the beta values
CLIMATE_FILE    = '../../GIS/bfa_ecozone.asc'
PFPR_FILE       = '../../GIS/bfa_pfpr_2to10.asc'
POPULATION_FILE = '../../GIS/bfa_pop.asc'
TREATMENT_FILE  = '../../GIS/bfa_treatment.asc'

# TODO Determine the bins computationally
populationBins = [797, 1417, 2279, 3668, 6386, 12627, 25584, 53601, 117418]
treatmentBins = [0.5, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9]


def getBin(value, bins):
    bins.sort()
    for item in bins:
        if value < item: return item
    if item >= max(bins):
        return max(bins)


def process():
    # Load the relevent data
    [ ascHeader, climate ] = load_asc(CLIMATE_FILE)
    [ ascHeader, pfpr ] = load_asc(PFPR_FILE)
    [ ascHeader, population ] = load_asc(POPULATION_FILE)
    [ ascHeader, treatment ] = load_asc(TREATMENT_FILE)

    # Prepare our results
    pfprRanges = {}
    zoneTreatments = {}

    # Process the data
    for row in range(0, ascHeader['nrows']):
        for col in range(0, ascHeader['ncols']):

            # Press on if there is nothing to do
            zone = climate[row][col]
            if zone == ascHeader['nodata']: continue

            # Note the bins
            popBin = getBin(population[row][col], populationBins)
            treatBin = getBin(treatment[row][col], treatmentBins)

            # Add to the dictionary as needed
            if zone not in pfprRanges:
                pfprRanges[zone] = {}            
            if popBin not in pfprRanges[zone]:
                pfprRanges[zone][popBin] = []
            if zone not in zoneTreatments:
                zoneTreatments[zone] = []
            
            # Add to our data sets
            pfprRanges[zone][popBin].append(pfpr[row][col])
            if treatBin not in zoneTreatments[zone]:
                zoneTreatments[zone].append(treatBin)

    return [ pfprRanges, zoneTreatments ]


def save(pfprRanges, zoneTreatments, filename):
    with open(filename, 'w') as script:
        # Print the front matter
        script.write("#!/bin/bash\n")
        script.write("\n# Calibration template script\n")
        
        # Print the blocks for the calibration
        for zone in pfprRanges.keys():    
            script.write("\nZONE={}\n".format(zone))
            values = " ".join(str(value) for value in sorted(pfprRanges[zone].keys()))
            script.write("for population in {}; do\n".format(values))
            values = " ".join(str(value) for value in sorted(zoneTreatments[zone]))
            script.write("  for treatment in {}; do\n".format(values))
            script.write("    for beta in `seq 0.05 0.05 1.20`; do\n")
            script.write("\n#TODO\n\n")
            script.write("    done\n")
            script.write("  done\n")
            script.write("done\n")


if __name__ == '__main__':
    # TODO Prompt for the relevent files / scan for the
    [ pfprRanges, zoneTreatments ] = process()

    # Print the relevent ranges for the user
    for zone in pfprRanges.keys():
        print "Climate Zone {}".format(zone)
        print "Treatments: {}".format(sorted(zoneTreatments[zone]))
        print "Populations: {}".format(sorted(pfprRanges[zone].keys()))
        for popBin in sorted(pfprRanges[zone].keys()):
            print "{} - {} to {} PfPR".format(popBin, min(pfprRanges[zone][popBin]), max(pfprRanges[zone][popBin]))
        print

    # Save the basic script
    save(pfprRanges, zoneTreatments, 'out/calibration.sh')
