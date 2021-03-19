#!/usr/bin/python3

# studyManager.py
# 
# Allows users to preform basic study management for the indicated configuration
# (i.e., project database)
import os
import sys
import argparse
import yaml
import psycopg2

sys.path.append(os.path.join(os.path.dirname(__file__), "include"))
import include.database as database
from include.calibrationLib import load_configuration


# Get a list of all the studies from the database
def get_studies(connectionString):
    sql = 'SELECT id, name FROM STUDY'
    return database.select(connectionString, sql, '')


# Add the indicated study to the database
def add_study(connectionString, studyName):
    sql = 'INSERT INTO study(Name) VALUES(%s) RETURNING id;'
    return database.insert_returning(connectionString, sql, {'Name': studyName})


def main(args):
    try:
        cfg = load_configuration(args.configuration)

        # Add the study if one was supplied
        if args.add is not None:
            studies = add_study(cfg["connection_string"], args.add)
            print(f"Study Id: {studies}")

        # Display the formated list of studies in the database
        if args.list:
            rows = get_studies(cfg["connection_string"])

            # Was nothing returned?
            if len(rows) == 0:
                print("No records returned")
                return

            # Display our resuts
            layout = "{!s:20} {!s:14}"
            print(layout.format("Study Name", "Study Id"))
            print("-"*34)
            for row in rows:
                print(layout.format(*(row[1], row[0])))

    except database.DatabaseError:
        # Defer to database library for error messages
        sys.exit(1)


if __name__ == "__main__":
    # Parse the parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--add', action='store', default=None)
    parser.add_argument('-c', action='store', dest='configuration')
    parser.add_argument('-l', '--list', action='store_true')    
    args = parser.parse_args()

    # Defer to main for everything else
    main(args)
