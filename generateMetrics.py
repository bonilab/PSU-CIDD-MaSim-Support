#!/usr/bin/python3

# generateMetrics.py
#
# This module contains functions relevent to getting metrics from ASC files.
import sys

from os import path

from include.ascFile import load_asc

# Note some constants
NUMERATOR = 0
DENOMINATOR = 1

def calculate(gisPath, prefix):

    # Attempt to load the files
    filename = "{}/{}_district.asc".format(gisPath, prefix)
    [ascheader, district] = load(filename, "district")        
    filename = "{}/{}_pfpr2to10.asc".format(gisPath, prefix)
    [_, pfpr] = load(filename, "PfPR")
    filename = "{}/{}_population.asc".format(gisPath, prefix)
    [_, population] = load(filename, "population")

    # Loop over the data that's been loaded
    data = {}
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

    # Write the weighted values to disk
    numerator = 0
    denominator = 0
    print("Saving data to: weighted_pfpr.csv")
    with open("weighted_pfpr.csv", 'w') as out:
        for key in sorted(data.keys()):
            numerator += data[key][NUMERATOR]
            denominator += data[key][DENOMINATOR]
            result = round((data[key][NUMERATOR] / data[key][DENOMINATOR]) * 100, 2)
            message = "District: {0}, PfPR: {1}%".format(int(key), result)
            
            out.write("{},{}\n".format(int(key), result))
            print(message)

    result = round(numerator * 100 / denominator, 2)
    print("\nFull Map, PfPR: {0}%".format(result))
    print("Population: {:,}\n".format(totalPopulation))


def load(filename, fileType):
    if not path.exists(filename):
        print("Could not find {} file, tried: {}".format(fileType, filename))
        exit(1)
    return load_asc(filename)    


if __name__ == '__main__':
    # Check the command line
    if len(sys.argv) != 3:
        print("Usage: ./generateMetrics [gis] [prefix]")
        print("gis - the path to the directory that the GIS files can be found in")
        print("prefix - the country code prefix used")
        print("\nExample ./generateMetrics.py ../GIS bfa")
        exit(0)

    # Parse the parameters
    gisPath = str(sys.argv[1])
    prefix = str(sys.argv[2])

    calculate(gisPath, prefix)