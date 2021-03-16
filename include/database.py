# database.py
#
# This module provides a wrapper for basic database functionality.
import sys
import psycopg2


def select(connectionString, sql, parameters):

    # Open the connection
    try:
        connection = psycopg2.connect(connectionString, connect_timeout=5)
        cursor = connection.cursor()

        # Execute the query, note the rows
        cursor.execute(sql, parameters)

        rows = cursor.fetchall()

        # Clean-up and return
        cursor.close()
        connection.close()

        return rows

    except psycopg2.OperationalError as err:
        sys.stderr.write(f'Error Connecting: Connection Timed out {err} ')

    except psycopg2.DatabaseError as e:
        sys.stderr.write(f'Database Error {e} ')
