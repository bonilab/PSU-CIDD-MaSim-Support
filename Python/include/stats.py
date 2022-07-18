# stats.py
#
# This module contains math functions and written with ASC files and NODATA values in mind.
import jenkspy
import numpy as np

# Find the goodness of variance fit (GVF) for the data set provided and the 
# number of classes (bins) indicated
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


# Smooth using a moving average with a sliding window
def movingAverage(vector, window):
    '''
    Calculate the moving average for the vector provided with the given window.

    vector - A set of values to calculate the moving average for.
    window - An odd-sized window to use when calculating the moving average.

    Returns a vector contain the moving average.
    '''
    if window < 1:
        raise ValueError('The window size should be greater than 1, got {}'.format(window))
    if window % 2 != 1:
        raise ValueError('Expected an odd window size, got {}'.format(window))

    length = len(vector)
    out = [0]*length
    for ndx in range(length):
        lb = int(ndx - (window - 1) / 2)
        rb = int(ndx + (window - 1) / 2)
        if lb < 0: lb = 0
        if rb > length: rb = length
        out[ndx] = (sum(vector[lb:rb]) / (rb - lb + 1))
    return out


def mse(expected, observed, nodata):
    total = 0
    count = 0
    for x in range(len(expected)):
        for y in range(len(expected[0])):
            if expected[x][y] == nodata: continue            
            total += pow(expected[x][y] - observed[x][y], 2)
            count += 1
    return total / count


def paddedMovingAverage(vector, padding, window):
    '''
    Pad the start and end of the vector before calculating the moving average 
    for the vector provided with the given window.

    vector - A set of values to calculate the moving average for.
    padding - The padding to use at the start and end of the vector.
    window - An odd-sized window to use when calculating the moving average.

    Returns a vector contain the moving average.
    '''
    # Force to a vector, create a new vector padded to the window size
    vector = vector.tolist()
    new_vector = vector[0:padding]
    new_vector.extend(vector)
    new_vector.extend(vector[-(padding + 1):-1])

    # Build a single array
    new_vector = movingAverage(new_vector, window)
    return new_vector[padding:-padding]


def weighted_avg(values, weights, nodata):    
    numerator  = 0
    denominator = 0
    for x in range(len(weights)):
        for y in range(len(weights[0])):
            if weights[x][y] == nodata: continue            
            numerator = (values[x][y] * weights[x][y])            
            denominator += weights[x][y]   
    return numerator / denominator
