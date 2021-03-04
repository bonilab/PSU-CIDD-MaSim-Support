# stats.py
#
# This module contains math functions and written with ASC files and NODATA values in mind.
import jenkspy
import numpy as np


def avg(values):
    total = 0
    count = 0
    for row in values:
        for value in row:
            total += value
            count += 1

    return total / count


# Find the goodness of variance fit (GVF) for the data set provided and the 
# number of classes (bins) indciated
#
# Source: https://stats.stackexchange.com/q/144075
def goodness_of_variance_fit(data, classes):
    # Find the break points and classify the data
    classes = jenkspy.jenks_breaks(data, classes)
    classified = np.array([classify(i, classes) for i in data])

    # Nested list of zone indices
    zone_indices = [[idx for idx, val in enumerate(classified) if zone + 1 == val] for zone in range(max(classified))]

    # Sum of squared deviations from array mean
    sdam = np.sum((data - np.mean(data)) ** 2)

    # Sorted polygon stats
    array_sort = [np.array([data[index] for index in zone]) for zone in zone_indices]

    # Sum of squared deviations of class means
    sdcm = sum([np.sum((classified - classified.mean()) ** 2) for classified in array_sort])

    # Calculate the GVF and return
    gvf = (sdam - sdcm) / sdam
    return gvf, classes

# Helper function for goodness_of_variance_fit, note that this presumes the 
# breaks are structured as follows: 
# [lower bound, 1st upper bound, 2nd upper bound, ..., nth upper bound]
def classify(value, breaks):
    for i in range(1, len(breaks)):
        if value < breaks[i]:
            return i
    return len(breaks) - 1


def mse(expected, observed, nodata):
    total = 0
    count = 0
    for x in range(len(expected)):
        for y in range(len(expected[0])):
            if expected[x][y] == nodata: continue            
            total += pow(expected[x][y] - observed[x][y], 2)
            count += 1
    return total / count


def weighted_avg(values, weights, nodata):    
    numerator  = 0
    denominator = 0
    for x in range(len(weights)):
        for y in range(len(weights[0])):
            if weights[x][y] == nodata: continue            
            numerator = (values[x][y] * weights[x][y])            
            denominator += weights[x][y]   
    return numerator / denominator
