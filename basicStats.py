# basicStats.py
#
# This module contains some basic math functions to use when evaluating results
# from the MaSim model. This module was written with ASC files and NODATA values
# in mind.

def avg(values):
    total = 0
    count = 0
    for row in values:
        for value in row:
            total += value
            count += 1

    return total / count


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
