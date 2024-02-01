#!/usr/bin/python3

# districtFilter.py
#
# Filter the indicated raster files by the district id values indicated.
import argparse
import os
import sys

# Import our libraries
sys.path.append(os.path.join(os.path.dirname(__file__), 'include'))
import include.ascFile as asc


def main(districtsFile, targetFiles, districts):
    # Load the reference districts raster
    [ascHeader, ascDistricts] = asc.load_asc(districtsFile)

    # Load the target extraction rasters
    rasters = []
    for file in targetFiles:
        _, data = asc.load_asc(file)
        rasters.append(data)

    # Iterate over the reference raster
    for row in range(ascHeader['nrows']):
        for col in range(ascHeader['ncols']):
            
            # Pass on no data
            if ascDistricts[row][col] == ascHeader['nodata']:
                continue
                
            # Pass if the district matches
            if ascDistricts[row][col] in districts:
                continue

            # This must not be a valid district, so replace it with no data
            for ndx in range(len(rasters)):
                rasters[ndx][row][col] = ascHeader['nodata']

    # Done, so save the data to disk, informing the user
    for ndx in range(len(targetFiles)):
        out = "extract_{}".format(targetFiles[ndx])
        print("Saving {} as {}".format(targetFiles[ndx], out))
        asc.write_asc(ascHeader, rasters[ndx], out)


if __name__ == "__main__":
    # Parse the parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', action='store', dest='districtsFile', required=True,
        help='Raster file that contains the district identification values')
    parser.add_argument('-t', action='store', dest='targetFile', nargs='*', required=True,
        help='Raster file(s) have to specified district(s) extracted')
    parser.add_argument('-i', action='store', dest='districts', nargs='*', required=True,
        help='The list of one or more district identification values to filter by')
    args = parser.parse_args()

    # Parse the districts to integers
    districts = [int(i) for i in args.districts]

    # Defer to main for everything else
    main(args.districtsFile, args.targetFile, districts)
