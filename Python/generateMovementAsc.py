#!/usr/bin/python3

# generateMovementAsc.py
# 
# Prompt the user to select a movement study and generate an aggregated ASC file
import argparse
import os
import sys

# Import our libraries
sys.path.append(os.path.join(os.path.dirname(__file__), "include"))
import include.ascFile as asc
from include.calibrationLib import load_configuration
from include.database import select, DatabaseError


SELECT_REPLICATES = """
SELECT r.id, c.filename, r.starttime, 
  CASE WHEN r.endtime IS null THEN 'Incomplete' ELSE 'Complete' END AS status
FROM sim.replicate r
  INNER JOIN sim.configuration c ON c.id = r.configurationid
WHERE r.movement = 'C' {}
ORDER BY r.starttime DESC"""

SELECT_MOVEMENTS = """
SELECT replicateid, count, x, y
FROM sim.location l INNER JOIN (
  SELECT replicateid, configurationid, sum(count) AS count, destination
  FROM sim.districtmovement dm
    INNER JOIN sim.replicate r ON r.id = dm.replicateid
  WHERE dm.replicateid = %(replicateId)s AND timestep = 31
  GROUP BY replicateid, configurationid, destination) iq ON l.configurationid = iq.configurationid AND l.index = iq.destination
"""

SELECT_ASC_HEADER = """
SELECT ncols, nrows, xllcorner, yllcorner, cellsize 
FROM sim.configuration c
  INNER JOIN sim.replicate r ON r.configurationid = c.id
WHERE r.id = %(replicateId)s"""

# Define the NODATA constant
NODATA = -9999


def generate_asc(connectionString, replicateId):
    # Query for the header data
    ascheader = asc.get_header()
    data = select(connectionString, SELECT_ASC_HEADER, {'replicateId':replicateId})
    if (len(data) != 1):
        print("An invlaid number of records ({}) was returned".format(len(data)))
        sys.exit(1)
    ascheader['ncols'] = data[0][0]
    ascheader['nrows'] = data[0][1]
    ascheader['xllcorner'] = data[0][2]
    ascheader['yllcorner'] = data[0][3]
    ascheader['cellsize'] = data[0][4]
    ascheader['nodata'] = NODATA
 
    # Prepare the matrix for the data
    ascdata = []
    for ndx in range(ascheader['nrows']):
        ascdata.append([NODATA] * ascheader['ncols'])

    # Query for the remainder of the data
    data = select(connectionString, SELECT_MOVEMENTS, {'replicateId':replicateId})
    for record in data:
        ascdata[record[2]][record[3]] = record[1]

    # Create the directory if need be
    if not os.path.isdir('out'): os.mkdir('out')

    # Write to disk and return the filename
    filename = "out/{}_movements.asc".format(replicateId)
    asc.write_asc(ascheader, ascdata, filename)
    return filename


# Display the list of replicates to the user and return the one they select
def prompt_user(connectionString, studyId):
    try:
        # Retrieve the replicates
        if (studyId is None):
            query = SELECT_REPLICATES.format('')
        else:
            query = SELECT_REPLICATES.format('AND c.studyid = %(studyId)s')
        replicates = select(connectionString, query, {'studyId':studyId})

        # Display them to the user
        if len(replicates) == 0:
            print("No replicates returned!")
            exit(0)
        print("Replicates returned: ")
        for replicate in replicates:
            print("{}\t{}\t{}\t{}".format(replicate[0], replicate[1], replicate[2], replicate[3]))

        # Prompt and return
        return int(input("Replicate to retrive or zero (0) to exit: "))

    except DatabaseError:
        sys.stderr.write("An unrecoverable database error occurred, exiting.\n")
        sys.exit(1)   


def main(configuration, studyId):
    # Prompt for the replicate to load
    cfg = load_configuration(configuration)
    replicateId = prompt_user(cfg["connection_string"], studyId)
    if replicateId == 0: exit(0)

    # Generate the ASC file, report the filename
    filename = generate_asc(cfg["connection_string"], replicateId)
    print("Results saved as: {}".format(filename))


if __name__ == "__main__":
    # Parse the parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', action='store', dest='configuration', required=True,
        help='The configuration file to reference when querying for movement study replicates')
    parser.add_argument('-s', action='store', dest='studyid', 
        help='The id of the study to use for the movement values, default none')
    args = parser.parse_args()

    # Define to the main function
    main(args.configuration, args.studyid)
