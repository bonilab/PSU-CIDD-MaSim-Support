# standards.py
#
# This module provides a place to store the standard values that should be used
# for projects.

# Templates for the expected reference files
DISTRICT_FILE   = "{}_district.asc"
PFPR_FILE       = "{}_pfpr2to10.asc"
POPULATION_FILE = "{}_population.asc"
WEIGHTED_PFPR   = "{}_weighted-pfpr.asc"

# Sentinel value to indicate that the values come from an ASC file
YAML_SENTINEL   = -1

# Standardized filenames for the beta map and epsilons
BETA_VALUES      = "out/{}_beta.asc"
EPSILON_VALUES   = "out/{}_epsilons.asc"