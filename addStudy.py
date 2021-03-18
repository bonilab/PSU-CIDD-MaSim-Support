# !/usr/bin/python3

# addStudy.py

# python addStudy.py -c rwa_configuration.yml -l
# python addStudy.py -c rwa_configuration.yml -a "studyName"

# Adding new studies to the database

# Import our libraries
import os
import sys
import argparse
import yaml
import psycopg2

sys.path.append(os.path.join(os.path.dirname(__file__), "include"))
from include.calibrationLib import *
from include.database import *


# List all studies
def get_studies(configuration):

    # return "List to populate"
    sql = 'SELECT id, name FROM STUDY'
    return select(configuration, sql, '')


# add studies
def add_study(configuration, stdName):

    sql = 'INSERT INTO study(Name) VALUES(%s) RETURNING id;'

    return insert_returning(configuration, sql, {'Name': stdName})


def main():
    # Parse the parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', action='store', dest='studyname', default=None)
    # parser.add_argument('-l', action='store', dest='projectname',default=None)
    parser.add_argument('-l', '--selectq', action='store_true', default=False)
    parser.add_argument('-c', action='store', dest='conf_file')
    args = parser.parse_args()
    insertStudy = args.studyname
    listStudy = args.selectq

    try:
        cfg = load_configuration(args.conf_file)

        if insertStudy:
            # insert
            studies = add_study(cfg["connection_string"], insertStudy)
            print("Study Id: " + str(studies))

        if listStudy:
            # select
            rows = get_studies(cfg["connection_string"])
            if len(rows) >= 1:
                for row in rows:
                    print("({},{})".format(row[1], row[0]))
            else:
                print("Table is empty, exiting")
                sys.exit(0)

    except DatabaseError:
        sys.stderr.write("An unrecoverable database error occurred, exiting.\n")
        sys.exit(1)


if __name__ == "__main__":
    # Check the command line
    if len(sys.argv) < 4:
        print("Usage: ./addStudy -c [configuration] [flag] [studyName]")
        print("configuration - the configuration file to be loaded")
        print("flag - the operation to be performed")
        print("studyName - the name of the study to be added")
        exit(0)

    main()