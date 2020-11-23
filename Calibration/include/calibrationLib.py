# calibrationLib.py
#
# This module includes functions that are intended for use with calibration functions.

import csv
import os

from database import *


# Path and name of file to save beta values to
BETAVALUES = 'data/calibration.csv'


# Get the bin that the value belongs to
def get_bin(value, bins):
    # Sort the bins and step through them
    bins.sort()
    for item in bins:
        if value < item:
            return item

    # For values greater than the largest bin, return that one
    if item >= max(bins):
        return max(bins)

    # Throw an error if we couldn't find a match (shouldn't happen)
    raise Exception("Matching bin not found for value: " + str(value))


# Read the relevent data from the CSV file into a dictionary
def load_betas(filename):
    lookup = {}
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:

            # Add a new entry for the zone
            zone = int(row['zone'])
            if not zone in lookup:
                lookup[zone] = {}

            # Add a new entry for the population
            population = float(row['population'])
            if not population in lookup[zone]:
                lookup[zone][population] = {}
            
            # Add a new entry for the treatment
            treatment = float(row['access'])
            if not treatment in lookup[zone][population]:
                lookup[zone][population][treatment] = []

            # Ignore the zeros unless the beta is also zero
            if float(row['pfpr']) == 0 and float(row['beta']) != 0: continue

            # Append the beta and PfPR
            lookup[zone][population][treatment].append([ float(row['pfpr']) / 100, float(row['beta']) ])

    return lookup


# Query the database at the given location for the beta values in the given 
# study. Note that we are presuming that the filenames have been standardized 
# to allow for scripting to take place.
#
# filterZero is an optional argument (default True) that prevents beta values 
#   associated with zero as a local minima from being returned.
def query_betas(connection, studyId, filterZero = True):
    
    # Permit beta = 0 when PfPR = 0, but filter the beta out otherwise since 
    # the PfPR should never quite reach zero during seasonal transmission
    SQL = """
        SELECT replicateid, zone, population, access, beta, eir, 
            CASE WHEN zone IN (0, 1) THEN max ELSE pfpr2to10 END AS pfpr,
            min, pfpr2to10, max
        FROM (
            SELECT replicateid, filename,
                cast((regexp_matches(filename, '^(\d*)-(\d*)-([\.\d]*)-([\.\d]*)'))[1] as integer) AS zone,
                cast((regexp_matches(filename, '^(\d*)-(\d*)-([\.\d]*)-([\.\d]*)'))[2] as integer) AS population,
                cast((regexp_matches(filename, '^(\d*)-(\d*)-([\.\d]*)-([\.\d]*)'))[3] as float) AS access,
                cast((regexp_matches(filename, '^(\d*)-(\d*)-([\.\d]*)-([\.\d]*)'))[4] as float) AS beta,
                avg(eir) AS eir, 
                min(pfpr2to10) AS min, 
                avg(pfpr2to10) AS pfpr2to10, 
                max(pfpr2to10) AS max
            FROM sim.configuration c
                INNER JOIN sim.replicate r on r.configurationid = c.id
                INNER JOIN sim.monthlydata md on md.replicateid = r.id
                INNER JOIN sim.monthlysitedata msd on msd.monthlydataid = md.id
            WHERE studyid = %(studyId)s AND md.dayselapsed >= (4352 - 366)
            GROUP BY replicateid, filename) iq {}           
        ORDER BY zone, population, access, pfpr"""
    header = "replicateid,zone,population,access,beta,eir,pfpr,min,pfpr2to10,max\n"

    # Include the filter if need be
    WHERE = "WHERE (beta = 0 and pfpr2to10 = 0) OR (beta != 0 and min != 0) "
    if filterZero:
        sql = SQL.format(WHERE)
    else:
        sql = SQL.format("")

    # Select for the beta values
    print("Loading beta values for study id: {}".format(studyId))
    rows = select(connection, sql, {'studyId': studyId})

    # Create the directory if need be
    if not os.path.isdir('data'): os.mkdir('data')

    # Save the values to a CSV file
    print("Saving beta values to: {}".format(BETAVALUES))
    with open(BETAVALUES, "wb") as csvfile:
        csvfile.write(header)
        for row in rows:
            line = ','.join(str(row[ndx]) for ndx in range(0, len(row)))
            csvfile.write("{}\n".format(line))