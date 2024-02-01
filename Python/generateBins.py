#!/usr/bin/python3

# generateBins.py
#
# This script generates the bins that need to be run to determine the beta values
import argparse

import os

import sys

# Import our libraries
sys.path.append(os.path.join(os.path.dirname(__file__), "include"))
import include.ascFile as asc
import include.calibrationLib as cl
import include.stats as stats
import include.bashWriter as bash


# Process the configuration file, GIS files, and produce the bins
def process(configuration, gisPath, prefix, type):
    # Load the configuration
    cfg = cl.load_configuration(configuration)

    # Load the data, remove the NODATA, and bin the population
    ascHeader, population = get_population(gisPath, prefix)
    data = list(i for j in population for i in j)
    data = list(i for i in data if i != ascHeader['nodata'])
    populationBreaks = bin_data(data, 'population')

    # Get the access to treatments rate and bin if need be
    treatments, needsBinning = cl.get_treatments_list(cfg, gisPath)
    if treatments == -1:
        raise Exception("Unable to load determine the treatments in the configuration.")
    if needsBinning:
        data = list(i for j in treatments for i in j)
        data = list(i for i in data if i != ascHeader['nodata'])
        treatments = bin_data(data, 'treatments')
    
    # Load the binning range type
    if type == 'pfpr':
        filename = "{}/{}_pfpr2to10.asc".format(gisPath, prefix)
    elif type == 'incidence':
        filename = "{}/{}_incidence.asc".format(gisPath, prefix)
    else:
        raise Exception("Unknown binning range type, {}".format(type))
    _, data = load(filename, "PfPR")
    
    # Load the climate and treatment rasters
    climate = cl.get_climate_zones(cfg, gisPath)
    treatment = cl.get_treatments_raster(cfg, gisPath)

    # Process the data
    rangeBins, zoneTreatments = {}, {}
    for row in range(0, ascHeader['nrows']):
        for col in range(0, ascHeader['ncols']):

            # Press on if there is nothing to do
            zone = climate[row][col]
            if zone == ascHeader['nodata']: continue

            # Note the bins
            popBin = int(cl.get_bin(population[row][col], populationBreaks))
            treatBin = cl.get_bin(treatment[row][col], treatments)

            # Add to the dictionary as needed
            if zone not in rangeBins:
                rangeBins[zone] = {}
            if popBin not in rangeBins[zone]:
                rangeBins[zone][popBin] = []
            if zone not in zoneTreatments:
                zoneTreatments[zone] = []

            # Add to our data sets
            rangeBins[zone][popBin].append(data[row][col])
            if treatBin not in zoneTreatments[zone]:
                zoneTreatments[zone].append(treatBin)

    return rangeBins, zoneTreatments, populationBreaks

# Helper function, get the correct population file
def get_population(gisPath, prefix):
    for name in ['population', 'init_pop']:
        filename = "{}/{}_{}.asc".format(gisPath, prefix, name)
        if os.path.exists(filename):
            return load(filename, "population")
    raise Exception("Could not find a population file in: {} with prefix '{}'".format(gisPath, prefix))

# Helper function, load the ASC file indicated
def load(filename, fileType):
    if not os.path.exists(filename):
        raise Exception("Could not find {} file, tried: {}".format(fileType, filename))
    return asc.load_asc(filename)    


# Bin the data provided using Jenks natural breaks optimization
def bin_data(data, type, minimumClasses=5, maximumClasses=30, delta=0.01):

    # Alert the user since this can take awhile for large data sets
    sys.stdout.write('Binning {}...'.format(type))
    sys.stdout.flush()

    # Iterate from the the minimum to the maximum number classes and 
    # return the breaks with the lowest goodness of variance fit (GVF)
    previousGvf = 0
    for classes in range(minimumClasses, maximumClasses + 1):
        gvf, breaks = stats.goodness_of_variance_fit(data, classes)
        if abs(previousGvf - gvf) <= delta:
            # Note that the first index contains the lower bound
            print('done!')
            return breaks[1:]
        previousGvf = gvf

    # If we get here, warn the user but press on
    print(classes, maximumClasses)
    if classes == maximumClasses:
        print("done!\nUnable to find optimal fit, classes = {}, GVF = {}".format(classes, gvf))
        return breaks[1:]
    

def main(args):
    # Check to see if it looks like there is a country prefix
    prefix = args.prefix
    if not prefix:
        prefix = cl.get_prefix(args.configuration)
        if prefix is None:
            print("Unknown or malformed country code prefix for configuration while parsing configuration name, {}".format(args.configuration))
            exit(cl.EXIT_FAILURE)

    # Check to make sure the type is valid
    if args.type == 'pfpr':
        label = 'PfPR'
    elif args.type == 'incidence':
        label = 'per 1000'
    else:
        print("Unknown type argument, {}".format(args.type))
        exit(cl.EXIT_SUCCESS)

    # Process and print the relevant ranges for the user
    try:
        [ranges, treatments, breaks] = process(args.configuration, args.gis, prefix, args.type)
        for zone in ranges.keys():
            if len(ranges.keys()) != 1: print("\nClimate Zone {}".format(int(zone)))
            print("Treatments: {}".format(sorted(treatments[zone])))
            print("Populations: {}".format(sorted(ranges[zone].keys())))
            for bin in sorted(ranges[zone].keys()):
                print("{} - {} to {} {}".format(bin, min(ranges[zone][bin]), max(ranges[zone][bin]), label))
            print

        # Save the bash script
        os.makedirs('out', exist_ok=True)
        if args.username: 
            bash.run_cluster(ranges, treatments, breaks, 'out/calibration.sh', prefix, args.username)
        else: 
            bash.run_local(ranges, treatments, breaks, 'out/calibration.sh', prefix)
            
    except Exception as ex:
        print(ex)
        exit(cl.EXIT_FAILURE)


if __name__ == '__main__':
    # Parse the parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', action='store', dest='configuration', required=True,
        help='The configuration file to reference when creating the bins')
    parser.add_argument('-g', action='store', dest='gis', required=True,
        help='The path to the directory that the GIS files can be found')
    parser.add_argument('-p', action='store', dest='prefix', 
        help='Optional, the file prefix for ASC files, if not supplied the script will attempt to determine it')
    parser.add_argument('-t', action='store', dest='type', required=False, default='pfpr',
        help='Optional, default \'pfpr\', the type of processing to be done either \'pfpr\' or \'incidence\'')
    parser.add_argument('-u', action='store', dest='username', required=False,
        help='Optional, if supplied scripts will be produced to run on the cluster with the user indicated')    
    args = parser.parse_args()

    # Defer to main
    main(args)
