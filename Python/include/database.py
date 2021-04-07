# database.py
#
# This module provides a wrapper for basic database functionality.
import sys
import psycopg2


# Custom error for us to throw
class DatabaseError(BaseException):
    pass


def select(connectionString, sql, parameters):
    '''Run a select operation on the database indicated by the connection string, with the given parameters.'''

    try:
        # Open the connection, override any timeout provided with something shorter
        # since we expect to be running interactively
        connection = psycopg2.connect(connectionString, connect_timeout=1)
        cursor = connection.cursor()

        # Execute the query, note the rows
        cursor.execute(sql, parameters)
        rows = cursor.fetchall()

        # Clean-up and return
        cursor.close()
        connection.close()
        return rows

    except psycopg2.OperationalError as err:
        sys.stderr.write(f'An error occurred connecting to the database: {err}')
        raise DatabaseError

    except psycopg2.DatabaseError as err:
        sys.stderr.write(f'A general database error occurred: {err}')
        raise DatabaseError


def insert_returning(connectionString, sql, parameters):
    '''Run an insert operation on the database that returns a value.'''

    try:
        # Open the connection, override any timeout provided with something shorter
        # since we expect to be running interactively
        connection = psycopg2.connect(connectionString, connect_timeout=1)
        cursor = connection.cursor()

        # Execute the query, note the rows
        cursor.execute(sql, parameters)
        returnValue = cursor.fetchone()[0]

        # Clean-up and return
        connection.commit()
        cursor.close()
        return returnValue

    except psycopg2.OperationalError as err:
        sys.stderr.write(f'An error occurred connecting to the database: {err}')
        raise DatabaseError

    except psycopg2.DatabaseError as err:
        sys.stderr.write(f'A general database error occurred: {err}')
        raise DatabaseError


def update(connectionString, sql, parameters):
    '''Run an update, insert, or delete operation on the database, return the number of rows effected.'''

    try:
        # Open the connection, override any timeout provided with something shorter
        # since we expect to be running interactively
        connection = psycopg2.connect(connectionString, connect_timeout=1)
        cursor = connection.cursor()

        # Execute the query, note the rows affected
        cursor.execute(sql, parameters)
        connection.commit()
        result = cursor.rowcount

        # Clean-up and return
        cursor.close()
        return result

    except psycopg2.OperationalError as err:
        sys.stderr.write(f'An error occurred connecting to the database: {err}')
        raise DatabaseError

    except psycopg2.DatabaseError as err:
        sys.stderr.write(f'A general database error occurred: {err}')
        raise DatabaseError
