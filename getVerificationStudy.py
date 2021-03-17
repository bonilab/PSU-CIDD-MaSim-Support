#!/usr/bin/python3

# getVerificationStudy.py
#
# Query for verification studies and prompt the use to supply the replicate 
# id that they wish to download, the CSV file saved is formatted so it can be 
# used with the Matlab plotting function.
import os
import sys

# Import our libraries
sys.path.append(os.path.join(os.path.dirname(__file__), "include"))

from include.calibrationLib import load_configuration
from include.database import select, DatabaseError


SELECT_REPLICATES = """
SELECT r.id, c.filename, 
    to_char(r.starttime, 'YYYY-MON-DD HH24:MI:SS'), 
    to_char(r.endtime, 'YYYY-MON-DD HH24:MI:SS')
FROM sim.study s 
    INNER JOIN sim.configuration c ON c.studyid = s.id
    INNER JOIN sim.replicate r ON r.configurationid = c.id
WHERE s.id = %(studyId)s
ORDER BY r.id ASC"""

SELECT_DATASET = """
SELECT dayselapsed, district, 
    sum(population) AS population,
    avg(msd.eir) AS eir,
    sum(population * pfprunder5) / sum(population) AS pfprunder5,
    sum(population * pfpr2to10) / sum(population) AS pfpr2to10,
    sum(population * pfprall) / sum(population) AS pfprall
FROM sim.replicate r
    INNER JOIN sim.configuration c ON c.id = r.configurationid
    INNER JOIN sim.monthlydata md ON md.replicateid = r.id
    INNER JOIN sim.monthlysitedata msd ON msd.monthlydataid = md.id
    INNER JOIN sim.location l ON l.id = msd.locationid
WHERE r.id = %(replicateId)s AND eir NOT IN (0, -9999)
GROUP BY dayselapsed, district"""


def main(configuration, studyId):
    try:
        # Load the configuration, query for the list of replicates
        cfg = load_configuration(configuration)
        replicates = select(cfg["connection_string"], SELECT_REPLICATES, {'studyId':studyId})

        # Display list, prompt user
        if len(replicates) == 0:
            print("No studies returned!")
            exit(0)

        print("Studies returned: ")
        for replicate in replicates:
            print("{}\t{}\t{}\t{}".format(replicate[0], replicate[1], replicate[2], replicate[3]))

        # Prompt for replicate id
        replicateId = int(input("Replicate to retrive: "))

        # Load the data set, exit if nothing is returned
        rows = select(cfg["connection_string"], SELECT_DATASET, {'replicateId':replicateId})
        if len(rows) == 0:
            print("No data returned!")
            exit(0)
    
        # Save the replicate to disk
        filename = "{}-verification-data.csv".format(replicateId)
        print("Saving data set to: {}".format(filename))
        with open(filename, "w") as csvfile:
            for row in rows:
                line = ','.join(str(row[ndx]) for ndx in range(0, len(row)))
                csvfile.write("{}\n".format(line))

    except DatabaseError:
        sys.stderr.write("An unrecoverable database error occurred, exiting.\n")
        sys.exit(1)


if __name__ == "__main__":
    # Check the command line
    if len(sys.argv) != 3:
        print("Usage: ./getVerificationStudy [configuration] [studyid]")
        print("configuration - the configuration file to be loaded")
        print("studyid - the database id of the verification studies")
        exit(0)

    # Parse the parameters
    configuration = str(sys.argv[1])
    studyId = int(sys.argv[2])

    # Run the main function
    main(configuration, studyId)