#!/usr/bin/python3

# generateBins.py
#
# This script generates the bins that need to be run to determine the beta values
import os
import re
import sys

# Import our libraries
sys.path.append(os.path.join(os.path.dirname(__file__), "include"))

from include.ascFile import load_asc
from include.calibrationLib import get_bin, get_climate_zones, get_treatments_list, get_treatments_raster, load_configuration
from include.stats import goodness_of_variance_fit


def process(configuration, gisPath, prefix):
    # Load the configuration
    cfg = load_configuration(configuration)

    # Load and bin the population
    filename = "{}/{}_population.asc".format(gisPath, prefix)
    [ascHeader, population] = load(filename, "population")
    data = list(i for j in population for i in j)
    data = list(i for i in data if i != ascHeader['nodata'])
    populationBreaks = bin_data(data)

    # Get the access to treatments rate and bin if need be
    [treatments, needsBinning] = get_treatments_list(cfg, gisPath)
    if treatments == -1:
        print("Unable to load determine the treatments in the configuration.")
        exit(1)
    if needsBinning:
        data = list(i for j in treatments for i in j)
        data = list(i for i in data if i != ascHeader['nodata'])
        treatments = bin_data(data)
    
    # Load the PfPR data
    filename = "{}/{}_pfpr2to10.asc".format(gisPath, prefix)
    [_, pfpr] = load(filename, "PfPR")

    # Load the climate and treatment rasters
    climate = get_climate_zones(cfg, gisPath)
    treatment = get_treatments_raster(cfg, gisPath)

    # Prepare our results
    pfprRanges = {}
    zoneTreatments = {}

    # Process the data
    for row in range(0, ascHeader['nrows']):
        for col in range(0, ascHeader['ncols']):

            # Press on if there is nothing to do
            zone = climate[row][col]
            if zone == ascHeader['nodata']:
                continue

            # Note the bins
            popBin = int(get_bin(population[row][col], populationBreaks))
            treatBin = get_bin(treatment[row][col], treatments)

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

    return [pfprRanges, zoneTreatments, populationBreaks]


# Helper function, load the ASC file indciated
def load(filename, fileType):
    if not os.path.exists(filename):
        print("Could not find {} file, tried: {}".format(fileType, filename))
        exit(1)
    return load_asc(filename)    


# Bin the data provided using Jenks natural breaks optimization
def bin_data(data, minimumClasses=5, maximumClasses=30, delta=0.01):

    # Iterate from the the minimum to the maximum number classes and 
    # return the breaks with the lowest goodness of variance fit (GVF)
    previousGvf = 0
    for classes in range(minimumClasses, maximumClasses + 1):
        gvf, breaks = goodness_of_variance_fit(data, classes)
        if abs(previousGvf - gvf) <= delta:
            # Note that the first index contains the lower bound
            return breaks[1:]
        previousGvf = gvf

    # If we get here, warn the user but press on
    print(classes, maximumClasses)
    if classes == maximumClasses:
        print("Unable to find optimal fit, classes = {}, GVF = {}".format(classes, gvf))
        return breaks[1:]


def save(pfpr, treatments, populationBreaks, filename, username):
    with open(filename, 'w') as script:
        # Print the front matter
        script.write("#!/bin/bash\n")
        script.write("source ./calibrationLib.sh\n\n")

        # Print the ASC file generation commands
        script.write("generateAsc \"\\\"{}\\\"\"\n".format(
            " ".join([str(x) for x in sorted(populationBreaks)])))
        script.write("generateZoneAsc \"\\\"{}\\\"\"\n\n".format(
            " ".join([str(x) for x in sorted(pfpr.keys())])))

        # Print the zone matter
        for zone in pfpr.keys():
            script.write("run {} \"\\\"{}\\\"\" \"\\\"{}\\\"\" {}".format(
                zone,
                " ".join([str(x) for x in sorted(populationBreaks)]),
                " ".join([str(x) for x in sorted(treatments[zone])]),
                username))


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: ./generateBins.py [configuration] [gis] [username]")
        print("configuration - the configuration file to be loaded")
        print("gis - the directory that GIS file can be found in")
        print("username - the user who will be running the calibration on the cluster")
        exit(0)

    # Parse the parameters
    configuration = str(sys.argv[1])
    gisPath = str(sys.argv[2])
    username = str(sys.argv[3])

    # Check to see if it looks like there is a country prefix
    prefix = re.search(r"^([a-z]{3})-.*\.yml", configuration)
    if prefix is None:
        print("Unknown or malformed country code prefix for configuration")
        exit(0)
    prefix = prefix.group(1)

    # Process and print the relevent ranges for the user
    [pfpr, treatments, populationBreaks] = process(configuration, gisPath, prefix)
    for zone in pfpr.keys():
        print("Climate Zone {}".format(zone))
        print("Treatments: {}".format(sorted(treatments[zone])))
        print("Populations: {}".format(sorted(pfpr[zone].keys())))
        for popBin in sorted(pfpr[zone].keys()):
            print("{} - {} to {} PfPR".format(popBin, min(pfpr[zone][popBin]), max(pfpr[zone][popBin])))
        print

    # Save the basic script
    if not os.path.isdir('out'):
        os.mkdir('out')
    save(pfpr, treatments, populationBreaks, 'out/calibration.sh', username)
