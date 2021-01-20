# database.py
#
# This module provides a wrapper for basic database functionality.
import psycopg2

def select(connection, sql, parameters):
    # Open the connection
    connection = psycopg2.connect(connection)
    cursor = connection.cursor()

    # Execute the query, note the rows
    cursor.execute(sql, parameters)
    rows = cursor.fetchall()

    # Clean-up and return
    cursor.close()
    connection.close()
    return rows