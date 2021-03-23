# database.py
#
# This module provides a wrapper for basic database functionality.
import sys
import psycopg2


# Custom error for us to throw
class DatabaseError(BaseException):
    pass


def select(connectionString, sql, parameters):
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


# Executes provided INSERT statement, and returns result of the operation
def insert_returning(connectionString, sql, parameters):
    try:
        # Open the connection, override any timeout provided with something shorter
        # since we expect to be running interactively
        connection = psycopg2.connect(connectionString, connect_timeout=1)
        cursor = connection.cursor()

        # Execute the query, note the rows
        cursor.execute(sql, (parameters['Name'],))
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


def remove_record(connectionString, sql, parameters):
    try:
        # Open the connection, override any timeout provided with something shorter
        # since we expect to be running interactively
        connection = psycopg2.connect(connectionString, connect_timeout=1)
        cursor = connection.cursor()

        # Execute the query, note the rows
        cursor.execute(sql, (parameters['id'],))

        # Clean-up and return
        connection.commit()
        # check if the study exists
        if cursor.rowcount:
            print("Study deleted successfully")
        else:
            print("Study does not exist")

        cursor.close()

    except psycopg2.OperationalError as err:
        sys.stderr.write(f'An error occurred connecting to the database: {err}')
        raise DatabaseError

    except psycopg2.DatabaseError as err:
        sys.stderr.write(f'A general database error occurred: {err}')
        raise DatabaseError

    except psycopg2.Error as e:
        print(type(e))
        print(e)


def rename_record(connectionString, sql, parameters):
    try:
        # Open the connection, override any timeout provided with something shorter
        # since we expect to be running interactively
        connection = psycopg2.connect(connectionString, connect_timeout=1)
        cursor = connection.cursor()

        # Execute the query, note the rows
        cursor.execute(sql, (parameters['name'], parameters['id'],))

        # Clean-up and return
        connection.commit()
        # check if the study exists
        if cursor.rowcount:
            print("Study renamed successfully")
        else:
            print("Study does not exist")

        cursor.close()

    except psycopg2.OperationalError as err:
        sys.stderr.write(f'An error occurred connecting to the database: {err}')
        raise DatabaseError

    except psycopg2.DatabaseError as err:
        sys.stderr.write(f'A general database error occurred: {err}')
        raise DatabaseError

    except psycopg2.Error as e:
        print(type(e))
        print(e)
