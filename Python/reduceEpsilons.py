#!/usr/bin/python3

# reduceEpsilons.py
#
# This module takes the inputs used by createBetaMap.py as well as the epsilon
# file to prepare. 
import argparse
import csv
import pathlib
import os
import stat
import sys

# Import our libraries
sys.path.append(os.path.join(os.path.dirname(__file__), "include"))

import include.calibrationLib as cl
from include.ascFile import load_asc
from include.utility import *

# Standardized reference files for the script
CALIBRATION = "data/calibration.csv"
POPULATION_FILE = "{}_population.asc"

# These are generated by createBetaMap, so should be present assuming the 
# correct country prefix is derived
BETAVALUES = "out/{}_beta.asc"
EPSILONVALUES = "out/{}_epsilons.asc"

# Default output
RESULTS = "out/reduction.csv"
SCRIPT = "out/script.sh"

parameters = {}


def addBeta(lookup, step, zone, beta, population, treatment):
    global parameters
    
    # Determine the population and treatment bin we are working with
    populationBin = int(cl.get_bin(population, lookup[zone].keys()))
    treatmentBin = cl.get_bin(treatment, lookup[zone][populationBin].keys())

    # Update the dictionary
    if zone not in parameters:
        parameters[zone] = {}
    if populationBin not in parameters[zone]:
        parameters[zone][populationBin] = {}
    if treatmentBin not in parameters[zone][populationBin]:
        parameters[zone][populationBin][treatmentBin] = set()

    # Add the stepped betas to the set
    value = round(beta - (step * 10), 4)
    while value < beta + (step * 10):
        # Only add values greater than zero
        if value > 0:
            parameters[zone][populationBin][treatmentBin].add(value)
        value = round(value + step, 4)
  

def getLookupBetas(lookup, zone, population, treatment):
    betas = set()
    for row in lookup[zone][population][treatment]:
        betas.add(row[1])
    return betas


def writeBetas(lookup, prefix, username):
    global parameters

    # Generate a list of populations to create ASC files for
    populationAsc = set()

    # Generate a list of betas to run (same format as missing.csv) that haven't been seen before
    reduced = []
    for zone in sorted(parameters.keys()):
        for population in sorted(parameters[zone].keys()):
            populationAsc.add(population)
            for treatment in sorted(parameters[zone][population]):
                betas = getLookupBetas(lookup, zone, population, treatment)
                for beta in sorted(parameters[zone][population][treatment]):
                    if beta not in betas:
                        reduced.append([int(zone), int(population), treatment, beta])

    # Double check to see if the list was cleared out
    if len(reduced) == 0:
        print("Nothing to reduce!")
        return

    # Save the missing values as a CSV file
    print("Preparing inputs, {}".format(RESULTS))
    with open(RESULTS, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(reduced)

    print("Preparing script, {}".format(SCRIPT))
    with open(SCRIPT, "w") as script:
        # Print the front matter
        script.write("#!/bin/bash\n")
        script.write("source ./calibrationLib.sh\n")
        script.write("checkDependencies {}\n".format(prefix))

        # Print the ASC file generation commands
        value = " ".join([str(int(x)) for x in sorted(populationAsc)])
        script.write("generateAsc \"\\\"{}\\\"\"\n".format(value.strip()))
        value = " ".join([str(int(x)) for x in sorted(parameters.keys())])
        script.write("generateZoneAsc \"\\\"{}\\\"\"\n".format(value.strip()))

        # Print the run command for the script
        script.write("runCsv '{}' {} {}\n".format(RESULTS[4:], prefix, username))

    # Set the file as executable
    script = pathlib.Path(SCRIPT)
    script.chmod(script.stat().st_mode | stat.S_IEXEC)        
        

def main(configuration, gisPath, tolerance, step, username):
    global parameters

    # Determine the country prefix
    prefix = cl.get_prefix(configuration)
    if prefix is None:
        sys.stderr.write("Invalid country code associated with configuration file: {}\n".format(configuration))
        sys.exit(1)

    # Load the configuration, and potentially raster data
    cfg = cl.load_configuration(configuration)
    climate = cl.get_climate_zones(cfg, gisPath)
    treatment = cl.get_treatments_raster(cfg, gisPath)

    # Load the relevent raster data
    filename = os.path.join(gisPath, POPULATION_FILE.format(prefix))    
    [ascheader, population] = load_asc(filename)
    lookup = cl.load_betas(CALIBRATION)

    # Read the epsilons file in
    [_, beta] = load_asc(BETAVALUES.format(prefix))
    [_, epsilon] = load_asc(EPSILONVALUES.format(prefix))

    print ("Evaluating epsilons for {} rows, {} columns".format(ascheader['nrows'], ascheader['ncols']))

    # Scan each of the epsilons
    for row in range(0, ascheader['nrows']):
        for col in range(0, ascheader['ncols']):
            # Pass on nodata
            value = epsilon[row][col]
            if value == ascheader['nodata']: continue

            # Pass when value is less than maximum
            if value < tolerance: continue

            # Update the running list
            addBeta(lookup, step, climate[row][col], beta[row][col], population[row][col], treatment[row][col])

        # Note the progress
        progressBar(row + 1, ascheader['nrows'])

    # Check to see if we are done
    if len(parameters) == 0:
        print("Nothing to reduce!")
    else:
        writeBetas(lookup, prefix, username)


if __name__ == "__main__":
    # Parse the parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', action='store', dest='configuration', required=True,
        help='The configuration file to reference when reducing the epsilon values')
    parser.add_argument('-g', action='store', dest='gis', required=True,
        help='The path to the directory that the GIS files can be found in')
    parser.add_argument('-t', action='store', dest='tolerance', required=True,
        help='float, maximum epsilon, should not be less than the step')       
    parser.add_argument('-s', action='store', dest='step', required=True,
        help='float, increment +/- 10x around known beta (maximum 0.00001)')
    parser.add_argument('-u', action='store', dest='username', required=True,
        help='The user who will be running the calibration on the cluster')
    args = parser.parse_args()
                
    # Check the step and tolerance
    tolerance = float(args.tolerance)
    step = float(args.step)
    if step >= 1:
        sys.stderr.write("The step cannot be greater than one\n")
        exit(1)
    if round(step, 5) != step:
        sys.stderr.write("{} exceeds maximum step of 0.00001\n".format(step))
        exit(1)
    if tolerance < step:
        sys.stderr.write("The tolerance, {}, is less than the step, {}\n".format(step, tolerance))
        exit(1)

    # Defer to main to do everything else
    main(args.configuration, args.gis, tolerance, step, args.username)