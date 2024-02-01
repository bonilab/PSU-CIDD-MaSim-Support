# calibrationLib.py
#
# This module includes functions that are intended for use with calibration functions.
import csv
import os
import re
import sys
import yaml

sys.path.append(os.path.join(os.path.dirname(__file__), "include"))
import ascFile as asc
import standards


# Define exit status codes
EXIT_SUCCESS, EXIT_FAILURE = 0, 1

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

    ascHeader, ascData = asc.load_asc(filename)
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
    
    Returns a matrix containing the climate zones, locations without a zone will use the common nodata value.
    '''

    # Start by checking if there is a raster defined, if so just load and return that
    if 'ecoclimatic_raster' in configurationYaml['raster_db']:
        filename = str(configurationYaml['raster_db']['ecoclimatic_raster'])
        filename = os.path.join(gisPath, filename)
        _, ascData = asc.load_asc(filename)
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
        exit(EXIT_FAILURE)

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
    if not (underFive == overFive == standards.YAML_SENTINEL):
        results = []
        if underFive != standards.YAML_SENTINEL:
            results.append(underFive)
        if overFive != standards.YAML_SENTINEL:
            results.append(overFive)
        return results, False

    # Get the unique under five treatments
    try:
        filename = str(configurationYaml['raster_db']['pr_treatment_under5'])
        filename = os.path.join(gisPath, filename)
        acsHeader, ascData = asc.load_asc(filename)
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
        _, ascData = asc.load_asc(filename)
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
    _, ascData = asc.load_asc(filename)
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

    Returns a matrix containing the climate zones, locations without a zone will use the common nodata value.
    '''

    # Start by checking if there is a raster defined, if so just load and return that
    if 'pr_treatment_under5' in configurationYaml['raster_db']:
        filename = str(configurationYaml['raster_db']['pr_treatment_under5'])
        filename = os.path.join(gisPath, filename)
        _, ascData = asc.load_asc(filename)
        return ascData

    # There is not, make sure there is a single value defined before continuing
    underFive = float(configurationYaml['raster_db']['p_treatment_for_less_than_5_by_location'][0])
    overFive = float(configurationYaml['raster_db']['p_treatment_for_more_than_5_by_location'][0])

    # There is not, make sure there is a single zone defined before continuing
    if underFive != overFive:
        print("Different treatments defined for under and over five, not supported.")
        exit(EXIT_FAILURE)

    # Generate and return the reference raster
    filename = str(configurationYaml['raster_db']['district_raster'])
    filename = os.path.join(gisPath, filename)
    return generate_raster(filename, underFive)


def load_betas(filename):
    '''
    Read the relevant data from the CSV file into a dictionary

    filename - The file, with or without the path attached, to be loaded
    '''

    lookup = {}
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)

        # Check to see if we are reading Under-5 or 2-10 PfPR values
        if 'pfpr2to10' in reader.fieldnames:
            pfpr = 'pfpr2to10'
        elif 'pfprunder5' in reader.fieldnames:
            pfpr = 'pfprunder5'
        else:
            raise Exception('Calibration data does not appear to have a valid PfPR header.')

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
            if float(row[pfpr]) == 0 and float(row['beta']) != 0: continue

            # Append the beta and PfPR
            lookup[zone][population][treatment].append([ float(row[pfpr]) / 100, float(row['beta']) ])

    return [pfpr, lookup]


def load_configuration(configuration):
    '''
    Load the configuration file provided and return the parsed YAML

    configuration - The YAML file, with or without the path, to be parsed.
    '''

    try:
        with open(configuration, "r") as yamlfile:
            cfg = yaml.safe_load(yamlfile)
            return cfg

    except yaml.parser.ParserError as ex:
        print("An error occurred parsing the input file:\n{}".format(ex))
        exit(EXIT_FAILURE)

    except FileNotFoundError:
        print("Configuration file not found: {}".format(configuration))
        exit(EXIT_FAILURE)

    except Exception as ex:
        print("An unknown error occurred while loading the configuration:\n{}".format(ex))
        exit(EXIT_FAILURE)
