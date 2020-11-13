#!/usr/bin/python

# createBetaMap.py
#
# This module reads an ASC file that contains the PfPR for the two to ten age
# bracket and generates three ASC files with beta values.

import csv

from include.ascFile import *
from include.calibrationLib import *
from include.utility import *

# TODO Grab all of this from a config file
# Connection string for the database
CONNECTION = "host=masimdb.vmhost.psu.edu dbname=rwanda user=sim password=sim"
PFPRVALUES = '../GIS/rwa_pfpr2to10.asc'
POPULATIONVALUES = '../GIS/rwa_population.asc'

# TODO RWA has only a single treatment rate and ecozone
TREATMENT = 0.99
ECOZONE = 0

# Starting epsilon and delta to be used
EPSILON = 0.00001
MAX_EPSILON = 0.1


def create_beta_map():
    # Load the relevent data
    [ ascheader, pfpr ] = load_asc(PFPRVALUES)
    [ ascheader, population ] = load_asc(POPULATIONVALUES)
    lookup = load_betas(BETAVALUES)

    # Prepare for the ASC data
    epsilons = []
    maxEpsilon = 0
    meanBeta = []

    # Prepare to track the distribution
    distribution = [0] * 5

    print "Determining betas for {} rows, {} columns".format(ascheader['nrows'], ascheader['ncols'])

    # Scan each of the rows 
    for row in range(0, ascheader['nrows']):

        # Append the empty rows
        epsilons.append([])
        meanBeta.append([])

        # Scan each of the PfPR values    
        for col in range(0, ascheader['ncols']):

            # Append nodata and continue
            if pfpr[row][col] == ascheader['nodata']:
                epsilons[row].append(ascheader['nodata'])
                meanBeta[row].append(ascheader['nodata'])
                continue

            # Get the beta values
            [values, epsilon] = get_betas(ECOZONE, pfpr[row][col], population[row][col], TREATMENT, lookup)

            # Update the distribution
            for exponent in range(1, len(distribution) + 1):
                if epsilon >= pow(10, -exponent):
                    distribution[exponent - 1] += 1
                    break

            # Was nothing returned?
            if len(values) == 0:
                epsilons[row].append(0)
                meanBeta[row].append(0)
                continue

            # Note the epsilon and the mean
            epsilons[row].append(epsilon)
            if epsilon > maxEpsilon: 
                maxEpsilon = epsilon
                maxValues = "PfPR: {}, Population: {}".format(pfpr[row][col], population[row][col])
            meanBeta[row].append(sum(values) / len(values))

        # Note the progress
        progressBar(row + 1, ascheader['nrows'])
                
    # Write the results
    print "\nMax epsilon: {} / {}".format(maxEpsilon, maxValues)
    print "Epsilon Distribution"
    for ndx in range(0, len(distribution)):
        print "{:>6} : {}".format(pow(10, -(ndx + 1)), distribution[ndx])
        total += distribution[ndx]
    print "Total Cells: {}".format(total)

    # Save the maps        
    print "\nSaving {}".format('out/epsilons_beta.asc')
    write_asc(ascheader, epsilons, 'out/epsilons_beta.asc')
    print "Saving {}".format('out/mean_beta.asc')
    write_asc(ascheader, meanBeta, 'out/mean_beta.asc')


# Get the beta values that generate the PfPR for the given population and 
# treatment level, this function will start with the lowest epsilon value 
# and increase it until at least one value is found to be returned
def get_betas(zone, pfpr, population, treatment, lookup):
    # Inital values
    epsilon = 0
    betas = []

    # Increase the epsilon until at least one value is found
    while len(betas) == 0:
        epsilon += EPSILON
        betas = get_betas_scan(zone, pfpr, population, treatment, lookup, epsilon)

        # Prevent an infinite loop, will result in an error
        if epsilon == MAX_EPSILON:
            print('Match not found!\nPfPR: ', pfpr, 'Population: ', population)
            return [None, None]

    # Return the results
    return [betas, epsilon] 


# Get the beta values that generate the PfPR for the given population and 
# treatment level, within the given margin of error.
def get_betas_scan(zone, pfpr, population, treatment, lookup, epsilon):

    # The zone is a bin, so it should just be there
    if not zone in lookup:
        raise ValueError("Zone {} was not found in lookup".format(zone))

    # Determine the population and treatment bin we are working with
    populationBin = get_bin(population, lookup[zone].keys())
    treatmentBin = get_bin(treatment, lookup[zone][populationBin].keys())
    
    # Note the bounds
    low = pfpr - epsilon
    high = pfpr + epsilon

    # Scan the PfPR values for the population and treatment level that are 
    # within the margin
    betas = []
    for value in lookup[zone][populationBin][treatmentBin]:

        # Add the value if it is in the bounds
        if low <= value[0] and value[0] <= high:
            betas.append(value[1])
            
        # We assume the data is stored, so break once the high value is less
        # than the current PfPR
        if high < value[0]: break

    # Return the betas collected
    return(betas)
    

# Main entry point for the script
def main(studyId):               
    query_betas(CONNECTION, studyId)
    create_beta_map()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: ./createBetaMap.py [study]"
        print "study - the database id of the study to use for the reference beta values"
        exit(0)

    # Parse the parameters
    studyId = int(sys.argv[1])    

    main(studyId)
