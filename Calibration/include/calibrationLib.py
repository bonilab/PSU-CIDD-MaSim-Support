# calibrationLib.py
#
# This module includes functions that are intended for use with calibration functions.

import csv


# Get the bin that the value belongs to
def get_bin(value, bins):
    # Sort the bins and step through them
    bins.sort()
    for item in bins:
        if value < item:
            return item

    # For values greater than the largest bin, return that one
    if item >= max(bins):
        return max(bins)

    # Throw an error if we couldn't find a match (shouldn't happen)
    raise Exception("Matching bin not found for value: " + str(value))


# Read the relevent data from the CSV file into a dictionary
def load_betas(filename):
    lookup = {}
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:

            # Add a new entry for the zone
            zone = int(row['zone'])
            if not zone in lookup:
                lookup[zone] = {}

            # Add a new entry for the population
            population = float(row['population'])
            if not population in lookup[zone]:
                lookup[zone][population] = {}
            
            # Add a new entry for the treatment
            treatment = float(row['access'])
            if not treatment in lookup[zone][population]:
                lookup[zone][population][treatment] = []

            # Ignore the zeros
            if float(row['pfpr']) == 0: continue

            # Append the beta and PfPR
            lookup[zone][population][treatment].append([ float(row['pfpr']) / 100, float(row['beta']) ])

    return lookup