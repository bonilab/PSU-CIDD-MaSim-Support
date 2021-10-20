# calibrationLib.py
#
# This module includes functions that are intended for use with calibration functions.
import csv
import os
import re
import sys
import yaml

sys.path.append(os.path.join(os.path.dirname(__file__), "include"))

from ascFile import load_asc
from database import select, DatabaseError

YAML_SENTINEL = -1

def get_bin(value, bins):
    '''Get the bin that the value belongs to'''

    # If the value is a bin, then return it
    if value in bins: return value

    # Sort the bins and step through them
    bins = sorted(bins)
    for item in bins:
        if value < item:
            return item

    # For values greater than the largest bin, return that one
    if item >= max(bins):
        return max(bins)

    # Throw an error if we couldn't find a match (shouldn't happen)
    raise Exception("Matching bin not found for value: " + str(value))


def get_prefix(filename):
    '''Get the three letter country code prefix from the filename'''

    prefix = re.search(r"^([a-z]{3})-.*\.yml", filename)
    if prefix is None:
        return None
    return prefix.group(1)


def generate_raster(filename, value):
    '''Generate a reference raster using the data in the filename and the value provided'''

    [ ascHeader, ascData ] = load_asc(filename)
    for row in range(0, ascHeader['nrows']):
        for col in range(0, ascHeader['ncols']):
            if ascData[row][col] == ascHeader['nodata']:
                continue
            ascData[row][col] = value
    return ascData



def get_climate_zones(configurationYaml, gisPath):
    '''
    Get the climate zones that are defined in the configuration.
    
    configurationYaml - The loaded configuration to examine.
    gisPath - The path to append to GIS files in the configuration.
    
    Returns a matrix contianing the climate zones, locations without a zone will use the common nodata value.
    '''

    # Start by checking if there is a raster defined, if so just load and return that
    if 'ecoclimatic_raster' in configurationYaml['raster_db']:
        filename = str(configurationYaml['raster_db']['ecoclimatic_raster'])
        filename = os.path.join(gisPath, filename)
        [_, ascData] = load_asc(filename)
        return ascData

    # Get the filename of the district raster in case we need it
    filename = str(configurationYaml['raster_db']['district_raster'])
    filename = os.path.join(gisPath, filename)

    # Are we looking at a version 4.1 configuration?
    yaml = configurationYaml['seasonal_info']
    if 'mode' in yaml.keys():
        # Is this a rainfall based configuration?
        if yaml['mode'] == 'rainfall':
            return generate_raster(filename, 1)

    # We are looking at an order configuration, if there is no raster then 
    # there should only be one climate zone
    if len(yaml["base"]) != 1:
        print("Multiple climate zones, but no raster defined.")
        exit(1)

    # Districts need to be defined, so use that as our template raster
    return generate_raster(filename, 1)


def get_treatments_list(configurationYaml, gisPath):
    '''
    Extract the treatments from the configuration that is supplied.

    configurationYaml - The loaded configuration to examine.
    gisPath - The path to append to GIS files in the configuration.

    Returns [results, needsBinning] where results are the parsed treatments and needsBinning indicates that the treatments need to be binned if True.
    '''

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
    try:
        filename = str(configurationYaml['raster_db']['pr_treatment_under5'])
        filename = os.path.join(gisPath, filename)
        [acsHeader, ascData] = load_asc(filename)
        underFive = list(set(i for j in ascData for i in j))
        underFive.remove(acsHeader['nodata'])
    except FileNotFoundError:
        # Warn and return when the U5 treatment rate cannot be opened
        sys.stderr.write("ERROR: Unable to open file associated with under five treatment rate: {}\n".format(filename))
        return None

    # Get the unique over five treatments
    try:
        filename = str(configurationYaml['raster_db']['pr_treatment_over5'])
        filename = os.path.join(gisPath, filename)
        [_, ascData] = load_asc(filename)
        overFive = list(set(i for j in ascData for i in j)) 
        overFive.remove(acsHeader['nodata'])
    except FileNotFoundError:
        # Warn and continue when the O5 rate cannot be opened
        sys.stderr.write("WARNING: Unable to open file associated with over five treatment rate: {}\n".format(filename))
        sys.stderr.write("WARNING: Continued without over five treatment rates.\n")
        overFive = []

    # Get the unique district ids
    filename = str(configurationYaml['raster_db']['district_raster'])
    filename = os.path.join(gisPath, filename)
    [_, ascData] = load_asc(filename)
    districts = list(set(i for j in ascData for i in j)) 
    districts.remove(acsHeader['nodata'])

    # If either treatment list is greater than districts, binning is needed
    # NOTE This is just a rough heuristic for the time being
    needsBinning = (len(underFive) > len(districts)) or (len(overFive) > len(districts))

    # Merge the under five and over five into a single set and return
    results = set(underFive + overFive)
    return results, needsBinning


def get_treatments_raster(configurationYaml, gisPath):
    '''
    Get the treatment raster that is defined in the configuration

    configurationYaml - The loaded configuration to examine.
    gisPath - The path to append to GIS files in the configuration.

    Returns a matrix contianing the climate zones, locations without a zone will use the common nodata value.
    '''

    # Start by checking if there is a raster defined, if so just load and return that
    if 'pr_treatment_under5' in configurationYaml['raster_db']:
        filename = str(configurationYaml['raster_db']['pr_treatment_under5'])
        filename = os.path.join(gisPath, filename)
        [_, ascData] = load_asc(filename)
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


def load_betas(filename):
    '''
    Read the relevent data from the CSV file into a dictionary

    filename - The file, with or without the path attached, to be loaded
    '''

    lookup = {}
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:

            # Add a new entry for the zone
            zone = int(float(row['zone']))
            if zone not in lookup:
                lookup[zone] = {}

            # Add a new entry for the population
            population = int(float(row['population']))
            if population not in lookup[zone]:
                lookup[zone][population] = {}
            
            # Add a new entry for the treatment
            treatment = float(row['access'])
            if treatment not in lookup[zone][population]:
                lookup[zone][population][treatment] = []

            # Ignore the zeros unless the beta is also zero
            if float(row['pfpr2to10']) == 0 and float(row['beta']) != 0: continue

            # Append the beta and PfPR
            lookup[zone][population][treatment].append([ float(row['pfpr2to10']) / 100, float(row['beta']) ])

    return lookup


def load_configuration(configuration):
    '''
    Load the configuration file provided and return the parsed YAML

    configuration - The YAML file, with or without the path, to be parsed.
    '''

    try:
        with open(configuration, "r") as yamlfile:
            cfg = yaml.load(yamlfile)
            return cfg

    except yaml.parser.ParserError as ex:
        print("An error occurred parsing the input file:\n{}".format(ex))
        exit(1)

    except FileNotFoundError:
        print("Configuration file not found: {}".format(configuration))
        exit(1)

    except Exception as ex:
        print("An unknown error occurred while loading the configuration:\n{}".format(ex))
        exit(1)


def query_betas(connection, studyId, filename="data/calibration.csv"):
    '''
    Query the database at the given location for the beta values in the given study. 
    Note that we are presuming that the filenames have been standardized to allow for scripting to take place.
    '''
    
    # Query for the one year mean EIR and PfPR along with binning parameters from the filename.
    SQL = r"""
        SELECT replicateid,
            cast(fileparts[1] as numeric) as zone,
            cast(fileparts[2] as numeric) as population,
            cast(fileparts[3] as numeric) as access,
            cast(fileparts[4] as numeric) as beta,
            eir,
            pfpr2to10
        FROM (
            SELECT replicateid,
                regexp_matches(filename, '^([\d\.]*)-(\d*)-([\.\d]*)-([\.\d]*)') as fileparts,
                avg(eir) AS eir, 
                avg(pfpr2to10) AS pfpr2to10
            FROM sim.configuration c
                INNER JOIN sim.replicate r on r.configurationid = c.id
                INNER JOIN sim.monthlydata md on md.replicateid = r.id
                INNER JOIN sim.monthlysitedata msd on msd.monthlydataid = md.id
            WHERE c.studyid = %(studyId)s
                AND md.dayselapsed BETWEEN 4015 AND 4380
            GROUP BY replicateid, filename) iq
        ORDER BY zone, population, access, pfpr2to10"""
    header = "replicateid,zone,population,access,beta,eir,pfpr2to10\n"

    try:
        # Select for the beta values
        print("Loading beta values for study id: {}".format(studyId))
        rows = select(connection, SQL, {'studyId': studyId})
    except DatabaseError:
        raise Exception("Error occurred while querying the database.")

    # Make sure results were returned
    if len(rows) == 0:
        raise ValueError("No data returned for study id: {}".format(studyId))

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
