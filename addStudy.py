# addStudy.py

#!/usr/bin/python3

# python addStudy.py -c rwa_configuration.yml -l
# python addStudy.py -c rwa_configuration.yml -a "studyName"

# addStudy.py
#
# Adding new studies to the database

# Import our libraries
import os
import sys
import argparse
import yaml
import psycopg2
from include.calibrationLib import *

# List all studies
def get_studies(configuration, studName):
    # return "List to populate"
    sql = '''SELECT * FROM STUDY'''

    return select(configuration["connection_string"], sql, {'name': None})

# add studies
def add_file(configuration, Name):
    Name = str(Name)

    sql = '''INSERT INTO study(Name) VALUES(%s) RETURNING id;'''

    return select(configuration["connection_string"], sql, {'Name': Name})

# connection
def select(connectionString, sql, parameters):
    # Open the connection
    connection = psycopg2.connect(connectionString)

    cursor = connection.cursor()
    # add study
    if (sql.find("INSERT") == 0):
        cursor.execute(sql, (parameters['Name'],))
        study_id = cursor.fetchone()[0]

        connection.commit()

        cursor.close()

        return study_id
    # list all studies
    if (sql.find("SELECT") == 0):
        cursor.execute(sql)

        rows = cursor.fetchall()
        for row in rows:
            print(row)
            # print(sql.find("SELECT"))
        cursor.close()


def main(configuration, flag, studyId):
    # Loading the configuration
    cfg = load_configuration(configuration)
    if (flag == 0):
        get_studies(cfg, studyId)
    if (flag == 1):
        studies = add_file(cfg, studyId)
        print("Study Id: " + str(studies))


if __name__ == "__main__":
    # Check the command line
    if len(sys.argv) < 4:
        print("Usage: ./addStudy [configuration] [flag] [studyid]")
        print("configuration - the configuration file to be loaded")
        print("flag - the operation to be performed")
        print("studyid - the database id of the verification studies")
        exit(0)

    # Parse the parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', action='store', dest='studyname', default=None)
    # parser.add_argument('-l', action='store', dest='projectname',default=None)
    parser.add_argument('-l', action='store_true', default=False)
    parser.add_argument('-c', action='store', dest='conf_file')
    args = parser.parse_args()
    # configuration=args.conf_file
    # studies=0

    if (sys.argv[3] == '-a'):
        main(args.conf_file, 1, args.studyname)
    if (sys.argv[3] == '-l'):
        main(args.conf_file, 0, '')

    # Run the main function
    ##cfg = load_configuration(args.conf_file)
    ##studies = add_file(cfg, args.studyname)
    ##print("ID is: "+str(studies))
    # configuration = str(sys.argv[1:])
    # print(configuration)