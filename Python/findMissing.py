#!/usr/bin/python3

# findMissing.py
#
# This script finds the combination that are missing from a calibration.
import csv
import os
import sys

from pathlib import Path

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


def main(filename, username):
    global missing, raw, population, treatment, beta

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
    print ("Saving {}".format(RESULTS))
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
    print("Preparing script, {}".format(SCRIPT))
    with open(SCRIPT, "w") as script:
        script.write("#!/bin/bash\n")
        script.write("source ./calibrationLib.sh\n")
        value = " ".join([str(x) for x in sorted(populations)])
        script.write("generateAsc \"\\\"{}\\\"\"\n".format(value.strip()))
        value = " ".join([str(x) for x in sorted(zones)])
        script.write("generateZoneAsc \"\\\"{}\\\"\"\n".format(value.strip()))
        script.write("runCsv '{}' {}\n".format(RESULTS, username))    


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: findMissing [calibration] [username]")
        print("calibration - the calibration file to be examined")
        print("username - the user who will be running the calibration on the cluster")
        exit(0)

    filename = str(sys.argv[1])
    username = str(sys.argv[2])
    main(filename, username)