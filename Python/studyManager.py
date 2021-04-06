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


# Get list of all the studies from the database
def get_studies(connectionString):
    sql = 'SELECT id, name FROM STUDY ORDER BY id ASC'
    return database.select(connectionString, sql, '')


# Add the indicated study to the database
def add_study(connectionString, studyName):
    sql = 'INSERT INTO study(Name) VALUES(%s) RETURNING id;'
    param = (studyName,)
    return database.insert_returning(connectionString, sql, param)


# Delete the indicated study from the database
def remove_study(configuration, stdid):
    sql = 'DELETE FROM study WHERE id = %s'
    param = (stdid,)
    return database.operationdb(configuration, sql, param)


# Rename the study in the database
def rename_studyname(configuration, stdid, newname):
    sql = 'UPDATE study SET name = %s WHERE id = %s'
    param = (newname, stdid,)
    return database.operationdb(configuration, sql, param)


def main(args):
    try:
        cfg = load_configuration(args.configuration)

        # Add the study if one was supplied
        if args.add is not None:
            studies = add_study(cfg["connection_string"], args.add)
            print(f"Study Id: {studies}")

        # Delete study
        if args.remove is not None:
            # delete
            remove_study(cfg["connection_string"], args.remove)

        # Rename study
        if args.update:
            id = args.update[0]
            sname = str(args.update[1])
            rename_studyname(cfg["connection_string"], id, sname)

        # Display the formated list of studies in the database
        if args.list:
            rows = get_studies(cfg["connection_string"])

            # Was nothing returned?
            if len(rows) == 0:
                print("No records returned")
                return

            # Display our resuts
            layout = "{!s:32} {!s:10}"
            print(layout.format("Study Name", "Study Id"))
            print("-"*42)
            for row in rows:
                print(layout.format(*(row[1], row[0])))

    except database.DatabaseError:
        # Defer to database library for error messages
        sys.exit(1)


if __name__ == "__main__":

    try:
        # Parse the parameters
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', action='store', dest='configuration', required=True)
        parser.add_argument('-a', '--add', action='store', default=None)
        parser.add_argument('-l', '--list', action='store_true', default=False)
        parser.add_argument('-d', '--delete', action='store', dest='remove', default=None)
        parser.add_argument('-u', '--update', default=[], nargs=2, dest='update')
        #parser.add_argument('-u', '--update', action='store_true', default=False)
        args = parser.parse_args()

    except:
        parser.print_help()
        sys.exit(1)
    # Defer to main for everything else
    main(args)
