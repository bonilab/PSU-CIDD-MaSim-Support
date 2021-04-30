#!/usr/bin/python3

import datetime 
import psycopg2

# Connection string for the database
CONNECTION = "host=masimdb.vmhost.psu.edu dbname=burkinafaso user=sim password=sim"

# Delete replicates attached to the calibration
REPLICATES = """
select r.id
from sim.configuration c
  inner join sim.replicate r on r.configurationid = c.id
where c.studyid in (12, 17)
"""

# Delete empty configuration
CONFIGURATIONS = """
SELECT c.id, c.studyid, c.filename
FROM sim.configuration c
  LEFT JOIN sim.replicate r on r.configurationid = c.id
WHERE r.id is null"""


def getResults(sql):
    # Open the connection
    connection = psycopg2.connect(CONNECTION)
    cursor = connection.cursor()

    # Execute the query, note the rows
    cursor.execute(sql)
    rows = cursor.fetchall()

    # Clean-up and return
    cursor.close()
    connection.close()

    return rows


def delete(sql, parameter):

    # Open the connection
    connection = psycopg2.connect(CONNECTION)
    connection.autocommit = True
    cursor = connection.cursor()

    # Run the query
    cursor.execute(sql, parameter)
    
    # Clean-up and return
    cursor.close()
    connection.close()


def deleteConfigurations():
  configurations = getResults(CONFIGURATIONS)
  for row in configurations:
    print("{} - Deleting configuration {}".format(datetime.datetime.now(), row[0]))
    delete("CALL delete_configuration(%(configurationId)s)", {'configurationId': row[0]})


def deleteReplicates():
  replicates = getResults(REPLICATES)
  for row in replicates:
    print("{} - Deleting replicate {}".format(datetime.datetime.now(), row[0]))
    delete("CALL delete_replicate(%(replicateId)s)", {'replicateId': row[0]})


if __name__ == '__main__':
  deleteReplicates()
  deleteConfigurations()

