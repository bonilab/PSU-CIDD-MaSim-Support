import os
import sys

from loader import *

# Import our libraries
sys.path.append(os.path.join(os.path.dirname(__file__), "include"))
from include.calibrationLib import *


def add_file(configuration, name):

    sql = ''' INSERT INTO study (name) VALUES (%(name)s)
    '''
    return select(configuration, sql, {'name' : name})


def main(configuration, studyId):

    # Loading the configuration
    cfg = load_configuration(configuration)
    studies = get_studies(cfg, studyId)


if __name__ == "__main__":
    # Check the command line
    if len(sys.argv) != 2:
        print("Usage: ./getVerificationStudy [configuration] [studyid]")
        print("configuration - the configuration file to be loaded")
        print("studyid - the database id of the verification studies")
        exit(0)

    # Parse the parameters
    configuration = str(sys.argv[1])
    studyId = int(sys.argv[2])

    # Run the main function
    main(configuration, studyId)