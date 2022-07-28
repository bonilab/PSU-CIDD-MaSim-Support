#!/usr/bin/python3

# deleteReplicates.py
#
# Perform administrative functions on the study database by deleting the 
# replicates in the indicated study, this will effectively remove that study
# from the database.
#
# NOTE that this script presumes that the database has been correctly updated 
# to allow deletion of completed replicates to take place.
import argparse
import datetime 
import os
import sys

# Import our libraries
sys.path.append(os.path.join(os.path.dirname(__file__), "include"))

from include.calibrationLib import load_configuration
from include.database import select, delete, DatabaseError


# Select the stalled (i.e., not running) replicates to be deleted
# NOTE Since this script cannot determine if they are still running on the ACI 
# or not, the assumption is that this will only be run when safe to do so.
SELECT_FAILED = """
SELECT r.id
FROM sim.replicate r
WHERE r.endtime is null"""

# Select the replicates to be deleted
SELECT_REPLICATES = """
select r.id
from sim.configuration c
  inner join sim.replicate r on r.configurationid = c.id
where c.studyid in (%(studyId)s)"""

# Select empty configurations, those that have no replicates associated with 
# them, so they may be deleted
SELECT_CONFIGURATIONS = """
SELECT c.id, c.studyid, c.filename
FROM sim.configuration c
  LEFT JOIN sim.replicate r on r.configurationid = c.id
WHERE r.id is null AND c.studyid > 2"""


def deleteConfigurations(connectionString):
  configurations = select(connectionString, SELECT_CONFIGURATIONS, None)
  for row in configurations:
    print("{} - Deleting configuration {}".format(datetime.datetime.now(), row[0]))
    delete(connectionString, "CALL delete_configuration(%(configurationId)s)", {'configurationId': row[0]})


def deleteFailed(connectionString):
  replicates = select(connectionString, SELECT_FAILED, None)
  for row in replicates:
    print("{} - Deleting replicate {}".format(datetime.datetime.now(), row[0]))
    delete(connectionString, "CALL delete_replicate(%(replicateId)s)", {'replicateId': row[0]})  


def deleteReplicates(connectionString, studyId):
  replicates = select(connectionString, SELECT_REPLICATES, {'studyId':studyId})
  for row in replicates:
    print("{} - Deleting replicate {}".format(datetime.datetime.now(), row[0]))
    delete(connectionString, "CALL delete_replicate(%(replicateId)s)", {'replicateId': row[0]})


def main(configuration, studyId, failed):
  try:
    cfg = load_configuration(configuration)
    print("Connection: {}".format(cfg['connection_string']))
    if failed:
      print("Deleting failed studies...")
      deleteFailed(cfg['connection_string'])
      
    if studyId is not None:
      # Guard against unintentional use
      print('\033[93m' + 'WARNING! Deleting from study {} will remove all failed replicates, and ALL replicates if the stored procedure bypasses completion checks!'.format(studyId) + '\033[0m')
      response = None
      while not response in ['Y', 'N']:
        response = input("Do you wish to continue? [Y/N] ").upper()
        if response == 'N':
          return

      # Delete the studies
      print("Deleting from study id {}...".format(studyId))
      deleteReplicates(cfg['connection_string'], studyId)

      # Don't delete configurations from the default study numbers
      if int(studyId) not in (1, 2): 
        print("Deleting configuration for study id {}...".format(studyId))
        deleteConfigurations(cfg['connection_string'])

  except DatabaseError:
    sys.stderr.write("An unrecoverable database error occurred, exiting\n")
    sys.exit(1)


if __name__ == '__main__':
  # Parse the arguments
  parser = argparse.ArgumentParser()
  parser.add_argument('-c', action='store', dest='configuration', required=True,
    help='The configuration file for the study to delete from')
  parser.add_argument('-f', action='store_true', dest='failed',
    help='Delete the failed or stalled replicates')    
  parser.add_argument('-s', action='store', dest='studyid', required=False,
    help='The id of the study to delete the replicates from')  
  args = parser.parse_args()
  
  # Defer to main
  main(args.configuration, args.studyid, args.failed)
