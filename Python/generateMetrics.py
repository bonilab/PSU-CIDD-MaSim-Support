#!/usr/bin/python3

# generateMetrics.py
#
# This module contains functions relevant to getting metrics from ASC files.
import argparse
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "include"))
from include.ascFile import load_asc

# Note some constants
NUMERATOR = 0
DENOMINATOR = 1

def calculate(gisPath, prefix, division, populationFilename=None):

    # Attempt to load the files
    filename = "{}/{}_{}.asc".format(gisPath, prefix, division)
    [ascheader, district] = load(filename, division)        
    filename = "{}/{}_pfpr2to10.asc".format(gisPath, prefix)
    [_, pfpr] = load(filename, "PfPR")

    if populationFilename is None:
        filename = "{}/{}_population.asc".format(gisPath, prefix)
    else:
        filename = populationFilename
    [_, population] = load(filename, "population")

    # Loop over the data that's been loaded
    data = {}
    cells = 0
    totalPopulation = 0
    for row in range(ascheader['nrows']):
        for col in range(ascheader['ncols']):
            # Continue if there is no data
            if district[row][col] == ascheader['nodata']:
                continue

            # Create the district if it does not exist
            key = district[row][col]
            if not key in data.keys():
                data[key] = [0, 0]

            # Update the running values
            data[key][NUMERATOR] += pfpr[row][col] * population[row][col]
            data[key][DENOMINATOR] += population[row][col]
            totalPopulation += population[row][col]
            cells += 1

    # Write the weighted values to disk
    numerator = 0
    denominator = 0
    filename = "weighted_pfpr_{}.csv".format(division)
    print("Saving data to: {}".format(filename))
    with open(filename, 'w') as out:
        for key in sorted(data.keys()):
            numerator += data[key][NUMERATOR]
            denominator += data[key][DENOMINATOR]
            result = round((data[key][NUMERATOR] / data[key][DENOMINATOR]) * 100, 2)
            message = "{}: {}, PfPR: {}%".format(division.capitalize(), int(key), result)
            
            out.write("{},{}\n".format(int(key), result))
            print(message)

    # Calculate the initial population if present
    initial = calculate_initial(gisPath, prefix)

    result = round(numerator * 100 / denominator, 2)
    print("\nFull Map, PfPR: {0}%".format(result))
    print("Population: {:,}".format(totalPopulation))
    if initial is not None:
        print("Initial Population: {:,}".format(initial))
    print("Cells: {}\n".format(cells))


def calculate_initial(gisPath, prefix):
    # Check to make sure the file exists
    filename = "{}/{}_init_pop.asc".format(gisPath, prefix)
    if not os.path.exists(filename):
        return None

    # Calculate and return the initial population value
    population = 0
    [ascheader, data] = load_asc(filename)
    for row in range(ascheader['nrows']):
        for col in range(ascheader['ncols']):
            if data[row][col] != ascheader['nodata']:
                population += data[row][col]
    return population


def load(filename, fileType):
    if not os.path.exists(filename):
        print("Could not find {} file, tried: {}".format(fileType, filename))
        exit(1)
    return load_asc(filename)    


if __name__ == '__main__':
    # Parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', action='store', dest='gis', required=True,
        help='The path to the directory that the GIS files can be found in')
    parser.add_argument('-p', action='store', dest='prefix', required=True,
        help='The country code prefix used')        
    parser.add_argument('-d', action='store', dest='division', default='district',
        help='(optional) District or province level metrics, default district')
    parser.add_argument('--pf', action='store', dest='population', default=None,
        help='(optional) Population file to use when summing the total population')
    args = parser.parse_args()

    # Check the parameters
    if args.division not in ("district", "province"):
        print("Unknown division: {}, expected 'district' or 'province'".format(args.division))
        sys.exit(1)
    if args.population is not None:
        print("Using population file: {}".format(args.population))
        calculate(args.gis, args.prefix, args.division, populationFilename = args.population)
    else:
        calculate(args.gis, args.prefix, args.division)