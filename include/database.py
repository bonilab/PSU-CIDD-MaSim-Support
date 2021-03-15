# database.py
#
# This module provides a wrapper for basic database functionality.
import sys
import psycopg2


def select(connectionString, sql, parameters):

    # Open the connection
    try:
        # connect_timeout for connectionString is 60 in the yml file
        connection = psycopg2.connect(connectionString, connect_timeout = 5)

    # operational error is raised when parameters passed to connect() are incorrect
    # or if the server runs out of memory

    except psycopg2.OperationalError as err:

        #print(f' Error Connecting : {err}')
        sys.stderr.write ('Error Connecting: Connection Timed out')
        # set connection to 'None' in case of error
        #connection = None

    # connection is successful
    #if connection is not None:

    cursor = connection.cursor()
    # catch exception for invalid SQL statement
    try:
        # Execute the query, note the rows
        cursor.execute(sql, parameters)

        # ProgrammingError happens when there is a syntax error in the SQL statement string passed
        # to the psycopg2 execute() method, or if a SQL statement is executed to delete a non-existent table,
        # or an attempt is made to create a table that already exists

    except psycopg2.ProgrammingError as e:
        #print(f' Syntax Error : {e}')
        sys.stderr.write('Syntax Error')
            # rollback to previous transaction before starting another
            #connection.rollback()

    rows = cursor.fetchall()

        # Clean-up and return
    cursor.close()
    connection.close()

    return rows