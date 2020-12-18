#!/usr/bin/env python
import preprocessing

#mysql = {
#    "host": "masimdb.vmhost.psu.edu",
#    "user": "sim",
#    "passwd": "sim",
#    "db": "rwanda",
#}

preprocessing_queue = [
#    preprocessing.scale_and_center,
#    preprocessing.dot_reduction,
#    preprocessing.connect_lines,
]

PFPRVALUES = '../../GIS/rwa_pfpr2to10.asc'
POPULATIONVALUES = '../../GIS/rwa_population.asc'

TREATMENT = 0.99
ECOZONE = 0

use_anonymous = True