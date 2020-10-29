# This module generates information on the difference in results between the
# reference PfPR 2 to 10 values and those of the model.

import csv

from include.ascFile import *
from include.basicStats import *

MODELVALUES = 'data/bf-11nb-bounded.csv'

FIELD = 'pfpr2to10'
OUTPUT = 'out/results.csv'

[ ascheader, pfpr ] = load_asc('data/cannon_pfpr.asc')
[ ascheader, population ] = load_asc('data/bounded_population.asc')

data = {}

def zeros(rows, cols):
    return [[0] * cols for _ in range(rows)]   

# Find all of the percent error values
with open(MODELVALUES) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:

        # Prepare to add the data
        dayselapsed = int(row['dayselapsed'])
        if not dayselapsed in data.keys():
            data[dayselapsed] = zeros(ascheader['nrows'], ascheader['ncols'])

        # Get the expected
        x = int(row['x'])
        y = int(row['y'])
        expected = pfpr[x][y]

        # Find the percent error
        observed = float(row[FIELD]) / 100
        pe = abs((observed - expected) / expected)

        # Update the data set
        data[dayselapsed][x][y] = pe


# Find the mean percent error for each time step
with open(OUTPUT, 'w') as results:

    # Print the header
    results.write("dayselapsed, average, weighted, mse\n")

    # Keep things sorted
    keys = data.keys()
    keys.sort()

    # Generate the results
    for key in keys:        
        
        out_avg = avg(data[key])
        out_weighted = weighted_avg(data[key], population, ascheader['nodata'])
        out_mse = mse(pfpr, data[key], ascheader['nodata'])

        msg = "{}, {}, {}, {}\n".format(key, out_avg, out_weighted, out_mse)
        results.write(msg)
    
