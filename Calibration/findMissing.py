#!/usr/bin/python

# findMissing.py
#
# This script finds the combination that are missing from a calibration.

import csv

BETAVALUES = 'data/calibration.csv'

RESULTS = 'out/missing.csv'

# Prepare the variables
population = set()
treatment = set()
beta = set()
missing = []
raw = []

def check(zone):
    global missing, population, treatment, beta

    # Check-in with user
    print "Checking zone {}".format(zone)

    # Unique values are loaded, sort them
    population = sorted(population, reverse=True)
    treatment = sorted(treatment)
    beta = sorted(beta)

    # Print how many we expect to find
    print "{} combinations expected".format(len(population) * len(treatment) * len(beta))

    # Scan for the matching row, add it to the missing list if not found
    for ndx in population:
        for ndy in treatment:
            for ndz in beta:
                row = [ ndx, ndy, ndz]
                matched = False
                for index in range(0, len(raw) - 1):
                    if row == raw[index]:
                        matched = True
                if not matched:
                    missing.append([zone, ndx, ndy, ndz])


def main():
    global missing, raw, population, treatment, beta

    # We aren't in a zone yet
    zone = None

    # Start by reading the raw population, treatment rate, and beta
    with open(BETAVALUES) as csvfile:
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
    print "{} combinations missing".format(len(missing))
    if len(missing) == 0: return

    # Save the missing values as a CSV file
    print "Saving {}".format(RESULTS)
    with open(RESULTS, "wb") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(missing)


if __name__ == "__main__":
    main()