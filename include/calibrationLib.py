# calibrationLib.py
#
# This module includes functions that are intended for use with calibration functions.
import csv
import os
import yaml

from include.ascFile import *
from include.database import *

YAML_SENTINEL = -1

# Get the bin that the value belongs to
def get_bin(value, bins):
    # If the value is a bin, then return it
    if value in bins: return value

    # Sort the bins and step through them
    bins = sorted(bins)
    for item in bins:
        if value < item: return item

    # For values greater than the largest bin, return that one
    if item >= max(bins): return max(bins)

    # Throw an error if we couldn't find a match (shouldn't happen)
    raise Exception("Matching bin not found for value: " + str(value))


# Generate a reference raster using the data in the filename and the value provided
def generate_raster(filename, value):
    [ ascHeader, ascData ] = load_asc(filename)
    for row in range(0, ascHeader['nrows']):
        for col in range(0, ascHeader['ncols']):
            if ascData[row][col] == ascHeader['nodata']: continue
            ascData[row][col] = value
    return ascData


# Get the climate zones that are defined in the configuration.
#
# configurationYaml - The loaded configuration to examine.
# gisPath - The path to append to GIS files in the configuration.
#
# Returns a matrix contianing the climate zones, locations without
#   a zone will use the common nodata value.
def get_climate_zones(configurationYaml, gisPath):
    # Start by checking if there is a raster defined, if so just load and return that
    if 'ecoclimatic_raster' in configurationYaml['raster_db']:
        filename = str(configurationYaml['raster_db']['ecoclimatic_raster'])
        filename = os.path.join(gisPath, filename)
        [ ascHeader, ascData ] = load_asc(filename)
        return ascData

    # There is not, make sure there is a single zone defined before continuing
    if len(configurationYaml["seasonal_info"]["base"]) != 1:
        print("Multiple climate zones, but no raster defined.")
        exit(1)

    # Get the zone value
    ecozone = len(configurationYaml["seasonal_info"]["base"]) - 1   # Zero indexed

    # Districts need to be defined, so use that as our template raster
    filename = str(configurationYaml['raster_db']['district_raster'])
    filename = os.path.join(gisPath, filename)
    return generate_raster(filename, ecozone)


# Extract the treatments from the configuration that is supplied.
#
# configurationYaml - The loaded configuration to examine.
# gisPath - The path to append to GIS files in the configuration.
#
# Returns [results, needsBinning] where results are the parsed treatments
#   and needsBinning indicates that the treatments need to be binned if True.
def get_treatments_list(configurationYaml, gisPath):
    # Start by checking the district level treatment values, note the zero index
    underFive = float(configurationYaml['raster_db']['p_treatment_for_less_than_5_by_location'][0])
    overFive = float(configurationYaml['raster_db']['p_treatment_for_more_than_5_by_location'][0])
    
    # If both are not equal to the sentinel then they are set via a raster
    if not (underFive == overFive == YAML_SENTINEL):
        results = []
        if underFive != YAML_SENTINEL:
            results.append(underFive)
        if overFive != YAML_SENTINEL:
            results.append(overFive)
        return results, False

    # Get the unique under five treatments
    filename = str(configurationYaml['raster_db']['pr_treatment_under5'])
    filename = os.path.join(gisPath, filename)
    [ ascHeader, ascData ] = load_asc(filename)
    underFive = list(set(i for j in ascData for i in j))
    underFive.remove(-9999)

    # Get the unique over five treatments
    filename = str(configurationYaml['raster_db']['pr_treatment_over5'])
    filename = os.path.join(gisPath, filename)
    [ ascHeader, ascData ] = load_asc(filename)
    overFive = list(set(i for j in ascData for i in j)) 
    overFive.remove(-9999)

    # Get the unique district ids
    filename = str(configurationYaml['raster_db']['district_raster'])
    filename = os.path.join(gisPath, filename)
    [ ascHeader, ascData ] = load_asc(filename)
    districts = list(set(i for j in ascData for i in j)) 
    districts.remove(-9999)

    # If either treatment list is greater than districts, binning is needed
    # NOTE This is just a rough heuristic for the time being
    needsBinning = (len(underFive) > len(districts)) or (len(overFive) > len(districts))

    # Merge the under five and over five into a single set and return
    results = set(underFive + overFive)
    return results, needsBinning


# Get the treatment raster that is defined in the configuration
#
# configurationYaml - The loaded configuration to examine.
# gisPath - The path to append to GIS files in the configuration.
#
# Returns a matrix contianing the climate zones, locations without
#   a zone will use the common nodata value.
def get_treatments_raster(configurationYaml, gisPath):
    # Start by checking if there is a raster defined, if so just load and return that
    if 'pr_treatment_under5' in configurationYaml['raster_db']:
        filename = str(configurationYaml['raster_db']['pr_treatment_under5'])
        filename = os.path.join(gisPath, filename)
        [ ascHeader, ascData ] = load_asc(filename)
        return ascData

    # There is not, make sure there is a single value defined before continuing
    underFive = float(configurationYaml['raster_db']['p_treatment_for_less_than_5_by_location'][0])
    overFive = float(configurationYaml['raster_db']['p_treatment_for_more_than_5_by_location'][0])

    # There is not, make sure there is a single zone defined before continuing
    if underFive != overFive:
        print("Different treatments defined for under and over five, not supported.")
        exit(1)

    # Generate and return the reference raster
    filename = str(configurationYaml['raster_db']['district_raster'])
    filename = os.path.join(gisPath, filename)
    return generate_raster(filename, underFive)


# Read the relevent data from the CSV file into a dictionary.
#
# filename - The file, with or without the path attached, to be loaded.
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


# Load the configuration file provided and return the parsed YAML
#
# configuration - The YAML file, with or without the path, to be parsed.
def load_configuration(configuration):
    try:
        with open(configuration, "r") as ymlfile:
            cfg = yaml.load(ymlfile)
            return cfg
    except Exception:
        print("Configuration file not found")
        exit(1)


# Query the database at the given location for the beta values in the given 
# study. Note that we are presuming that the filenames have been standardized 
# to allow for scripting to take place.
#
# filterZero is an optional argument (default True) that prevents beta values 
#   associated with zero as a local minima from being returned.
def query_betas(connection, studyId, filterZero = True, filename = "data/calibration.csv"):
    
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
    directory = os.path.dirname(os.path.abspath(filename))
    if not os.path.isdir(directory): os.mkdir(directory)

    # Save the values to a CSV file
    print("Saving beta values to: {}".format(filename))
    with open(filename, "w") as csvfile:
        csvfile.write(header)
        for row in rows:
            line = ','.join(str(row[ndx]) for ndx in range(0, len(row)))
            csvfile.write("{}\n".format(line))