# database.py
#
# This module provides a wrapper for basic database functionality.
import sys
import psycopg2


def select(connectionString, sql, parameters):

    flag = False
    # Open the connection
    try:
        # overriding connect_timeout to reduce wait time and exit in case of exception
        connection = psycopg2.connect(connectionString, connect_timeout=5)
        cursor = connection.cursor()

        # Execute the query, note the rows
        cursor.execute(sql, parameters)

        rows = cursor.fetchall()

        flag = True

        # Clean-up and return
        cursor.close()
        connection.close()

        return rows

    except psycopg2.OperationalError as err:
        sys.stderr.write(f'An error occurred connecting to the database: {err} ')


    except psycopg2.DatabaseError as e:
        sys.stderr.write(f'Database Error: {e} ')

    if not flag:
        raise SystemExit



