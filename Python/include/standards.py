# standards.py
#
# This module provides a place to store the standard values that should be used
# for projects.

# Templates for the expected reference files
DISTRICT_FILE   = "{}_district.asc"
PFPR_FILE       = "{}_pfpr2to10.asc"
POPULATION_FILE = "{}_population.asc"

# Sentinel value to indicate that the values come from an ASC file
YAML_SENTINEL   = -1

# Standardized filenames for the beta map and epsilons
BETAVALUES      = "out/{}_beta.asc"
EPSILONVALUES   = "out/{}_epsilons.asc"