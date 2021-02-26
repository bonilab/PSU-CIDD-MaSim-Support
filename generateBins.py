#!/usr/bin/python3
# generateBins.py
#
# This script generates the bins that need to be run to determine the beta values
import os
import sys

# Import our libraries
sys.path.append(os.path.join(os.path.dirname(__file__), "include"))

from ascFile import *
from calibrationLib import *


# TODO Still need a good way of supplying these
PFPR_FILE = "rwa_pfpr2to10.asc"
POPULATION_FILE = "rwa_population.asc"

# TODO Determine the bins computationally
# Following bins are for Rwanda
POPULATION_BINS = [2125, 5640, 8989, 12108, 15577, 20289, 27629, 49378, 95262, 286928]


def process(configuration, gisPath=""):
    # Load the configuration
    cfg = load_configuration(configuration)
    filename = os.path.join(gisPath, PFPR_FILE)

    # TODO Add the stuff for the population bins!
    # GVF Implementation
    binning = bin_asc(filename)

    list_bins = []
    list_GVF = []
    # Assuming the range for bins to be between 5 and 30 (computing the optimal number of bins w.r.t. GVF), to avoid overfitting or underfitting of data
    for x in range(5, 30):
        GVF = goodness_of_variance_fit(binning, x)
        # GVF less than 0.7 might not be the best fit for data; GVF ~ 0 (No fit), GVF ~ 1 (Perfect fit)
        if GVF < 0.7:
            print ("Bins=", x,"GVF = ", GVF, "Warning: GVF too low")
        # Storing the values of bins and GVF in a list
        list_bins.append(x)
        list_GVF.append(GVF)
    # computing difference between GVF values and storing them as (key, value) pairs in dictionary
    diff_GVF = {list_bins[i]: abs(list_GVF[i] - list_GVF[i - 1]) for i in range(len(list_bins))}
    for key, value in diff_GVF.items():
        # taking such value of bin for which the difference between consecutive GVF values is greater than or equal to 0.1
        if value >= 0.1:
            print("Total number of bins", key)
            # corresponding to the computed bin(key), finding the value of GVF
            GVF = goodness_of_variance_fit(binning, key)
            print("The value of Goodness of variance fit", GVF)

    # Get the access to treatments rate
    [treatments, needsBinning] = get_treatments_list(cfg, gisPath)
    if treatments == -1:
        print("Unable to load determine the treatments in the configuration.")
        exit(1)

    # TODO Add stuff for binning the treatments as needed!
    if needsBinning:
        print("Treatments need binning, not currently supported")
        exit(1)

    # Load the climate and treatment rasters
    climate = get_climate_zones(cfg, gisPath)
    treatment = get_treatments_raster(cfg, gisPath)

    # Load the relevent data
    filename = os.path.join(gisPath, PFPR_FILE)
    [ascHeader, pfpr] = load_asc(filename)
    filename = os.path.join(gisPath, POPULATION_FILE)
    [ascHeader, population] = load_asc(filename)

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
            popBin = int(get_bin(population[row][col], POPULATION_BINS))
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

    return [pfprRanges, zoneTreatments]


def save(pfpr, treatments, filename, username):
    with open(filename, 'w') as script:
        # Print the front matter
        script.write("#!/bin/bash\n")
        script.write("source ./calibrationLib.sh\n\n")

        # Print the ASC file generation commands
        script.write("generateAsc \"\\\"{}\\\"\"\n".format(
            " ".join([str(x) for x in sorted(POPULATION_BINS)])))
        script.write("generateZoneAsc \"\\\"{}\\\"\"\n\n".format(
            " ".join([str(x) for x in sorted(pfpr.keys())])))

        # Print the zone matter
        for zone in pfpr.keys():
            script.write("run {} \"\\\"{}\\\"\" \"\\\"{}\\\"\" {}".format(
                zone,
                " ".join([str(x) for x in sorted(POPULATION_BINS)]),
                " ".join([str(x) for x in sorted(treatments[zone])]),
                username))


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: ./generateBins.py [configuration] [username] [gis]")
        print("configuration - the configuration file to be loaded")
        print("gis - the directory that GIS file can be found in")
        print("username - the user who will be running the calibration on the cluster")
        exit(0)

    # Parse the parameters
    configuration = str(sys.argv[1])
    gisPath = str(sys.argv[2])
    username = str(sys.argv[3])

    # Process and print the relevent ranges for the user
    [pfpr, treatments] = process(configuration, gisPath)
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
    save(pfpr, treatments, 'out/calibration.sh', username)
