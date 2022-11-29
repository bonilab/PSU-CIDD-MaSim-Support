#!/usr/bin/python3

# findMissing.py
#
# This script finds the combination that are missing from a calibration.
import argparse
import csv
import sys

# Output file paths
RESULTS = "missing.csv"
SCRIPT = "script.sh"

# Prepare the variables
population = set()
treatment = set()
beta = set()
missing = []
raw = []

def check(zone):
    global missing, population, treatment, beta

    # Check-in with user
    print ("Checking zone {}".format(zone))

    # Unique values are loaded, sort them
    population = sorted(population, reverse=True)
    treatment = sorted(treatment)
    beta = sorted(beta)

    # Print how many we expect to find
    print ("{} combinations expected".format(len(population) * len(treatment) * len(beta)))

    # Scan for the matching row, add it to the missing list if not found
    for ndx in population:
        for ndy in treatment:
            for ndz in beta:
                row = [ ndx, ndy, ndz]
                matched = False
                for index in range(len(raw)):
                    if row == raw[index]:
                        matched = True
                        break
                if not matched:
                    missing.append([zone, ndx, ndy, ndz])


def main(filename, country, username):
    global missing, raw, population, treatment, beta

    # Check to make sure the file seems correct
    if not filename.endswith('.csv'):
        sys.stderr.write("File, {}, does not appear to be a CSV file, exiting\n".format(filename))
        sys.exit(1)

    # We aren't in a zone yet
    zone = None

    # Start by reading the raw population, treatment rate, and beta
    with open(filename) as csvfile:

        reader = csv.DictReader(csvfile)
        for row in reader:
            # Set the zone if not set
            if zone is None:
                zone = row['zone']

            # Are we in a new block?
            if zone != row['zone']:
                check(zone)
                raw = []
                population = set()
                treatment = set()
                beta = set()
                zone = row['zone']

            # Set the values
            population.add(row['population'])
            treatment.add(row['access'])
            beta.add(row['beta'])
            raw.append([row['population'], row['access'], row['beta']])

    # Check the last zone
    check(zone)
    
    # Print the number missing
    print ("{} combinations missing".format(len(missing)))
    if len(missing) == 0: return

    # Save the missing values as a CSV file
    print("Generating files...")
    print("Saving: {}".format(RESULTS))
    with open(RESULTS, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(missing)

    # Parse out the unique values for the script
    zones = set()
    populations = set()
    for row in range(1, len(missing)):
        zones.add(missing[row][0])
        populations.add(missing[row][1])

    # Save the script to disk
    print("Saving: {}".format(SCRIPT))
    with open(SCRIPT, "w") as script:
        script.write("#!/bin/bash\n")
        script.write("source ./calibrationLib.sh\n")
        value = " ".join([str(x) for x in sorted(populations)])
        script.write("generateAsc \"\\\"{}\\\"\"\n".format(value.strip()))
        value = " ".join([str(x) for x in sorted(zones)])
        script.write("generateZoneAsc \"\\\"{}\\\"\"\n".format(value.strip()))
        script.write("runCsv '{}' {} {}\n".format(RESULTS, country, username))    


if __name__ == "__main__":
    # Parse the parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', action='store', dest='calibration', required=True,
        help='The cached calibration values file (*.csv) to scan for missing values')
    parser.add_argument('-i', action='store', dest='country', required=True,
        help='The three letter country code for the study')
    parser.add_argument('-u', action='store', dest='username', required=True,
        help='The username for the user that is running the calibration')
    args = parser.parse_args()

    main(args.calibration, args.country, args.username)